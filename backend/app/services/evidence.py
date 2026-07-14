from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from ..models import AgentRun, Approval, AuditEvent, WorkflowRun
from ..schemas import EvidencePackage, IntakeRequest
from .agent_engine import AgentResult
from .hashing import sha256_json, sha256_text


def new_evidence_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"BADS-{stamp}-{uuid4().hex[:8].upper()}"


def create_run(db: Session, payload: IntakeRequest, result: AgentResult) -> WorkflowRun:
    run_id = str(uuid4())
    evidence_id = new_evidence_id()
    input_payload = payload.model_dump(mode="json")
    input_hash = sha256_json(input_payload)
    output_payload = {
        "lead_score": result.lead_score,
        "risk_level": result.risk_level,
        "confidence": result.confidence,
        "summary": result.summary,
        "proposal": result.proposal,
        "backlog": result.backlog,
        "flags": result.flags,
    }
    output_hash = sha256_json(output_payload)

    run = WorkflowRun(
        id=run_id,
        evidence_id=evidence_id,
        company=payload.company,
        contact=str(payload.contact),
        request_text=payload.request_text,
        source_type=payload.source_type,
        data_classification=payload.data_classification,
        status="awaiting_approval",
        lead_score=result.lead_score,
        risk_level=result.risk_level,
        confidence=result.confidence,
        summary=result.summary,
        proposal=result.proposal,
        backlog=result.backlog,
        flags=result.flags,
        input_hash=input_hash,
        output_hash=output_hash,
        model_provider=result.model_provider,
        model_name=result.model_name,
        estimated_cost_usd=result.estimated_cost_usd,
    )
    db.add(run)

    default_stages: list[dict[str, object]] = [
        {
            "agent_name": "Intake Agent",
            "decision_summary": "Request normalized and validated.",
            "confidence": result.confidence,
            "flags": [],
        },
        {
            "agent_name": "Qualification Agent",
            "decision_summary": f"Lead score {result.lead_score}; risk {result.risk_level}.",
            "confidence": result.confidence,
            "flags": [],
        },
        {
            "agent_name": "Proposal Agent",
            "decision_summary": "Commercial pilot draft generated.",
            "confidence": result.confidence,
            "flags": [],
        },
        {
            "agent_name": "Project Agent",
            "decision_summary": f"{len(result.backlog)} backlog items generated.",
            "confidence": result.confidence,
            "flags": [],
        },
        {
            "agent_name": "Evidence Agent",
            "decision_summary": f"Evidence package {evidence_id} sealed for approval.",
            "confidence": result.confidence,
            "flags": result.flags,
        },
    ]
    stages = result.stage_summaries or default_stages
    previous_hash = input_hash
    for stage in stages:
        agent_name = str(stage["agent_name"])
        decision_summary = str(stage["decision_summary"])
        stage_confidence = float(stage.get("confidence", result.confidence))
        stage_flags = list(stage.get("flags", []))
        agent_output_hash = sha256_text(f"{agent_name}|{decision_summary}|{output_hash}")
        db.add(
            AgentRun(
                id=str(uuid4()),
                workflow_run_id=run_id,
                agent_name=agent_name,
                decision_summary=decision_summary,
                confidence=stage_confidence,
                input_hash=previous_hash,
                output_hash=agent_output_hash,
                flags=stage_flags,
            )
        )
        previous_hash = agent_output_hash

    approval = Approval(
        id=str(uuid4()),
        workflow_run_id=run_id,
        status="pending",
        proposed_action="draft_email",
        external_side_effect=True,
    )
    db.add(approval)
    db.add(
        AuditEvent(
            id=str(uuid4()),
            workflow_run_id=run_id,
            event_type="workflow_created",
            actor="system",
            details={
                "evidence_id": evidence_id,
                "input_hash": input_hash,
                "output_hash": output_hash,
                "approval_required": True,
                "agent_count": len(stages),
            },
        )
    )
    db.commit()
    db.refresh(run)
    return run


def build_evidence_package(run: WorkflowRun) -> EvidencePackage:
    approval = run.approval
    agent_runs = [
        {
            "agent_name": item.agent_name,
            "agent_version": item.agent_version,
            "status": item.status,
            "decision_summary": item.decision_summary,
            "confidence": item.confidence,
            "input_hash": item.input_hash,
            "output_hash": item.output_hash,
            "flags": item.flags,
            "started_at": item.started_at.isoformat(),
            "completed_at": item.completed_at.isoformat(),
        }
        for item in run.agent_runs
    ]
    core = {
        "evidence_id": run.evidence_id,
        "workflow_id": run.workflow_id,
        "workflow_version": run.workflow_version,
        "created_at": run.created_at.isoformat(),
        "input_hash": run.input_hash,
        "output_hash": run.output_hash,
        "approval_status": approval.status,
    }
    package_hash = sha256_json(core)
    return EvidencePackage(
        evidence_id=run.evidence_id,
        workflow_id=run.workflow_id,
        workflow_version=run.workflow_version,
        created_at=run.created_at,
        input={
            "source_type": run.source_type,
            "content_hash": run.input_hash,
            "data_classification": run.data_classification,
        },
        agent_runs=agent_runs,
        proposed_action={
            "type": approval.proposed_action,
            "risk_level": run.risk_level,
            "external_side_effect": approval.external_side_effect,
        },
        approval={
            "required": approval.required,
            "status": approval.status,
            "reviewer_id": approval.reviewer_id,
            "reviewed_at": approval.reviewed_at,
            "review_note": approval.review_note,
        },
        outcome={
            "status": run.status,
            "executed_at": None,
            "result_hash": None,
        },
        integrity={
            "package_hash": package_hash,
            "input_hash": run.input_hash,
            "output_hash": run.output_hash,
            "retention_policy": "pilot-default-v1",
        },
    )
