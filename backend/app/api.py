from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from .database import get_db
from .models import Approval, AuditEvent, WorkflowRun
from .schemas import (
    ApprovalDecision,
    DashboardSummary,
    EvidencePackage,
    IntakeRequest,
    WorkflowRunRead,
)
from .security import require_api_key
from .services.agent_engine import AgentEngine
from .services.evidence import build_evidence_package, create_run


def run_query():
    return select(WorkflowRun).options(
        joinedload(WorkflowRun.approval),
        selectinload(WorkflowRun.agent_runs),
        selectinload(WorkflowRun.audit_events),
    )


def build_router(settings) -> APIRouter:
    bound = APIRouter(dependencies=[Depends(require_api_key)])

    @bound.post("/intake", response_model=WorkflowRunRead, status_code=status.HTTP_201_CREATED)
    def create_intake_bound(payload: IntakeRequest, db: Session = Depends(get_db)) -> WorkflowRun:
        engine = AgentEngine(settings)
        result = engine.process(
            company=payload.company,
            request_text=payload.request_text,
            data_classification=payload.data_classification,
        )
        return create_run(db, payload, result)

    @bound.get("/runs", response_model=list[WorkflowRunRead])
    def list_runs(
        limit: int = Query(default=50, ge=1, le=200),
        db: Session = Depends(get_db),
    ) -> list[WorkflowRun]:
        statement = run_query().order_by(WorkflowRun.created_at.desc()).limit(limit)
        return list(db.scalars(statement).unique().all())

    @bound.get("/runs/{run_id}", response_model=WorkflowRunRead)
    def get_run(run_id: str, db: Session = Depends(get_db)) -> WorkflowRun:
        run = db.scalars(run_query().where(WorkflowRun.id == run_id)).unique().one_or_none()
        if run is None:
            raise HTTPException(status_code=404, detail="Workflow run not found")
        return run

    @bound.get("/approvals", response_model=list[WorkflowRunRead])
    def list_pending_approvals(db: Session = Depends(get_db)) -> list[WorkflowRun]:
        statement = (
            run_query()
            .join(WorkflowRun.approval)
            .where(Approval.status == "pending")
            .order_by(WorkflowRun.created_at.asc())
        )
        return list(db.scalars(statement).unique().all())

    @bound.post("/approvals/{approval_id}/decision", response_model=WorkflowRunRead)
    def decide_approval(
        approval_id: str,
        payload: ApprovalDecision,
        db: Session = Depends(get_db),
    ) -> WorkflowRun:
        approval = db.scalar(select(Approval).where(Approval.id == approval_id))
        if approval is None:
            raise HTTPException(status_code=404, detail="Approval not found")
        if approval.status != "pending":
            raise HTTPException(status_code=409, detail="Approval has already been decided")

        approval.status = payload.decision
        approval.reviewer_id = payload.reviewer_id
        approval.review_note = payload.note
        approval.reviewed_at = datetime.now(timezone.utc)
        run = db.get(WorkflowRun, approval.workflow_run_id)
        if run is None:
            raise HTTPException(status_code=404, detail="Workflow run not found")
        run.status = {
            "approved": "approved_draft",
            "rejected": "rejected",
            "revision": "revision_requested",
        }[payload.decision]
        db.add(
            AuditEvent(
                id=str(uuid4()),
                workflow_run_id=run.id,
                event_type="approval_decided",
                actor=payload.reviewer_id,
                details={"decision": payload.decision, "note": payload.note},
            )
        )
        db.commit()
        return db.scalars(run_query().where(WorkflowRun.id == run.id)).unique().one()

    @bound.get("/evidence/{evidence_id}", response_model=EvidencePackage)
    def get_evidence(evidence_id: str, db: Session = Depends(get_db)) -> EvidencePackage:
        run = db.scalars(run_query().where(WorkflowRun.evidence_id == evidence_id)).unique().one_or_none()
        if run is None:
            raise HTTPException(status_code=404, detail="Evidence package not found")
        return build_evidence_package(run)

    @bound.get("/dashboard/summary", response_model=DashboardSummary)
    def dashboard_summary(db: Session = Depends(get_db)) -> DashboardSummary:
        total = db.scalar(select(func.count()).select_from(WorkflowRun)) or 0
        awaiting = db.scalar(
            select(func.count()).select_from(WorkflowRun).where(WorkflowRun.status == "awaiting_approval")
        ) or 0
        approved = db.scalar(
            select(func.count()).select_from(WorkflowRun).where(WorkflowRun.status == "approved_draft")
        ) or 0
        rejected = db.scalar(
            select(func.count()).select_from(WorkflowRun).where(
                WorkflowRun.status.in_(["rejected", "revision_requested"])
            )
        ) or 0
        avg_score = db.scalar(select(func.avg(WorkflowRun.lead_score))) or 0.0
        avg_confidence = db.scalar(select(func.avg(WorkflowRun.confidence))) or 0.0
        return DashboardSummary(
            total_runs=int(total),
            awaiting_approval=int(awaiting),
            approved=int(approved),
            rejected_or_revision=int(rejected),
            average_lead_score=round(float(avg_score), 2),
            average_confidence=round(float(avg_confidence), 3),
        )

    return bound
