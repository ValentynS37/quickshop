from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class IntakeRequest(BaseModel):
    company: str = Field(min_length=2, max_length=200)
    contact: EmailStr
    request_text: str = Field(min_length=20, max_length=20_000)
    source_type: Literal["manual", "web_form", "email", "api"] = "manual"
    data_classification: Literal["public", "internal", "confidential", "restricted"] = "internal"


class AgentProfileRead(BaseModel):
    name: str
    role: str
    execution: str
    active: bool
    external_actions_allowed: bool = False


class AgentRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    agent_name: str
    agent_version: str
    status: str
    decision_summary: str
    confidence: float
    input_hash: str
    output_hash: str
    flags: list[str]
    started_at: datetime
    completed_at: datetime


class ApprovalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    required: bool
    status: str
    proposed_action: str
    external_side_effect: bool
    reviewer_id: str | None
    review_note: str | None
    reviewed_at: datetime | None
    created_at: datetime


class WorkflowRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    evidence_id: str
    workflow_id: str
    workflow_version: str
    company: str
    contact: str
    request_text: str
    source_type: str
    data_classification: str
    status: str
    lead_score: int
    risk_level: str
    confidence: float
    summary: str
    proposal: str
    backlog: list[dict[str, object]]
    flags: list[str]
    input_hash: str
    output_hash: str
    model_provider: str
    model_name: str
    estimated_cost_usd: float
    created_at: datetime
    updated_at: datetime
    approval: ApprovalRead
    agent_runs: list[AgentRunRead]


class ApprovalDecision(BaseModel):
    decision: Literal["approved", "rejected", "revision"]
    reviewer_id: str = Field(min_length=2, max_length=120)
    note: str | None = Field(default=None, max_length=2000)


class DashboardSummary(BaseModel):
    total_runs: int
    awaiting_approval: int
    approved: int
    rejected_or_revision: int
    average_lead_score: float
    average_confidence: float


class EvidencePackage(BaseModel):
    evidence_id: str
    workflow_id: str
    workflow_version: str
    created_at: datetime
    input: dict[str, object]
    agent_runs: list[dict[str, object]]
    proposed_action: dict[str, object]
    approval: dict[str, object]
    outcome: dict[str, object]
    integrity: dict[str, object]
