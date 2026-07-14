from __future__ import annotations

import json
import os
from typing import Any, Literal, TypeVar

from pydantic import BaseModel, Field

from ..config import Settings


class IntakeAnalysis(BaseModel):
    lead_score: int = Field(ge=0, le=100)
    risk_level: Literal["low", "medium", "high"]
    confidence: float = Field(ge=0, le=1)
    summary: str
    missing_information: list[str] = Field(default_factory=list)
    flags: list[str] = Field(default_factory=list)


class ResearchBrief(BaseModel):
    workflow_recommendation: str
    data_requirements: list[str]
    assumptions: list[str]
    risks: list[str]


class SalesDraft(BaseModel):
    proposal: str
    package_name: str
    next_step: str
    commercial_risks: list[str] = Field(default_factory=list)


class BacklogItem(BaseModel):
    title: str
    acceptance: str
    priority: Literal["high", "medium", "low"]


class ProjectPlan(BaseModel):
    backlog: list[BacklogItem] = Field(min_length=3, max_length=10)


class QAReview(BaseModel):
    passed: bool
    confidence: float = Field(ge=0, le=1)
    issues: list[str] = Field(default_factory=list)
    flags: list[str] = Field(default_factory=list)


class EvidenceReview(BaseModel):
    evidence_summary: str
    approval_required: bool = True
    flags: list[str] = Field(default_factory=list)


class AgentsWorkflowOutput(BaseModel):
    lead_score: int
    risk_level: str
    confidence: float
    summary: str
    proposal: str
    backlog: list[dict[str, object]]
    flags: list[str]
    estimated_cost_usd: float = 0.0
    stage_summaries: list[dict[str, object]] = Field(default_factory=list)


OutputT = TypeVar("OutputT", bound=BaseModel)


class AgentsWorkflow:
    """Code-orchestrated OpenAI Agents SDK workflow for BADS OS."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.total_tokens = 0

    def run(self, *, company: str, request_text: str, data_classification: str) -> AgentsWorkflowOutput:
        self._configure_runtime()
        from agents import Agent, set_tracing_disabled

        set_tracing_disabled(not self.settings.agent_tracing_enabled)
        model = self.settings.openai_model

        intake_agent = Agent(
            name="BADS Intake Agent",
            model=model,
            output_type=IntakeAnalysis,
            instructions=(
                "Analyze one business automation request. Extract the business need, score pilot fit, "
                "classify risk, and identify missing information. Never make legal, tax, payment, "
                "employment, medical, investment, or safety-critical decisions. Return Ukrainian output."
            ),
        )
        research_agent = Agent(
            name="BADS Research Agent",
            model=model,
            output_type=ResearchBrief,
            instructions=(
                "Design a bounded automation workflow from the provided request and intake analysis. "
                "List data requirements, assumptions, and risks. Do not browse or invent private facts. "
                "All external actions must remain behind human approval. Return Ukrainian output."
            ),
        )
        sales_agent = Agent(
            name="BADS Sales Agent",
            model=model,
            output_type=SalesDraft,
            instructions=(
                "Prepare a concise pilot proposal based only on the supplied request and analysis. "
                "Do not promise autonomous external actions or unsupported capabilities. Return Ukrainian output."
            ),
        )
        project_agent = Agent(
            name="BADS Project Agent",
            model=model,
            output_type=ProjectPlan,
            instructions=(
                "Turn the supplied workflow into an implementation backlog with measurable acceptance criteria. "
                "Keep the first pilot narrow and human-in-the-loop. Return Ukrainian output."
            ),
        )
        qa_agent = Agent(
            name="BADS QA Agent",
            model=model,
            output_type=QAReview,
            instructions=(
                "Review the proposed workflow, proposal, and backlog for contradictions, unsafe autonomy, "
                "missing approvals, and unsupported claims. Return Ukrainian output."
            ),
        )
        evidence_agent = Agent(
            name="BADS Evidence Agent",
            model=model,
            output_type=EvidenceReview,
            instructions=(
                "Summarize what must be recorded in the evidence trail for this workflow. "
                "Require human approval for any external side effect. Do not expose secrets. Return Ukrainian output."
            ),
        )

        base_input = (
            f"Company: {company}\n"
            f"Data classification: {data_classification}\n"
            f"Request: {request_text}"
        )
        intake = self._run_agent(intake_agent, base_input, IntakeAnalysis)
        research = self._run_agent(
            research_agent,
            self._json_input(base_input=base_input, intake=intake.model_dump()),
            ResearchBrief,
        )
        sales = self._run_agent(
            sales_agent,
            self._json_input(
                base_input=base_input,
                intake=intake.model_dump(),
                research=research.model_dump(),
            ),
            SalesDraft,
        )
        project = self._run_agent(
            project_agent,
            self._json_input(
                base_input=base_input,
                research=research.model_dump(),
                sales=sales.model_dump(),
            ),
            ProjectPlan,
        )
        qa = self._run_agent(
            qa_agent,
            self._json_input(
                base_input=base_input,
                intake=intake.model_dump(),
                research=research.model_dump(),
                sales=sales.model_dump(),
                project=project.model_dump(),
            ),
            QAReview,
        )
        evidence = self._run_agent(
            evidence_agent,
            self._json_input(
                base_input=base_input,
                intake=intake.model_dump(),
                research=research.model_dump(),
                sales=sales.model_dump(),
                project=project.model_dump(),
                qa=qa.model_dump(),
            ),
            EvidenceReview,
        )

        flag_values = [*intake.flags, *qa.flags, *evidence.flags]
        if not qa.passed:
            flag_values.append("qa_review_failed")
        if evidence.approval_required:
            flag_values.append("human_approval_required")
        flags = self._dedupe(flag_values)
        confidence = round((intake.confidence + qa.confidence) / 2, 3)
        summary = (
            f"{intake.summary}\n\nРекомендований workflow: {research.workflow_recommendation}\n\n"
            f"Evidence: {evidence.evidence_summary}"
        )
        proposal = f"{sales.proposal}\n\nНаступний крок: {sales.next_step}"

        stage_summaries = [
            {
                "agent_name": "BADS Coordinator",
                "decision_summary": "Specialist agents executed in a controlled sequence.",
                "confidence": confidence,
                "flags": [],
            },
            {
                "agent_name": "Intake Agent",
                "decision_summary": intake.summary,
                "confidence": intake.confidence,
                "flags": intake.flags,
            },
            {
                "agent_name": "Research Agent",
                "decision_summary": research.workflow_recommendation,
                "confidence": confidence,
                "flags": research.risks,
            },
            {
                "agent_name": "Sales Agent",
                "decision_summary": f"{sales.package_name}: {sales.next_step}",
                "confidence": confidence,
                "flags": sales.commercial_risks,
            },
            {
                "agent_name": "Project Agent",
                "decision_summary": f"{len(project.backlog)} backlog items generated.",
                "confidence": confidence,
                "flags": [],
            },
            {
                "agent_name": "QA Agent",
                "decision_summary": "QA passed." if qa.passed else "; ".join(qa.issues),
                "confidence": qa.confidence,
                "flags": qa.flags,
            },
            {
                "agent_name": "Evidence Agent",
                "decision_summary": evidence.evidence_summary,
                "confidence": confidence,
                "flags": evidence.flags,
            },
        ]

        return AgentsWorkflowOutput(
            lead_score=intake.lead_score,
            risk_level=intake.risk_level,
            confidence=confidence,
            summary=summary,
            proposal=proposal,
            backlog=[item.model_dump() for item in project.backlog],
            flags=flags,
            estimated_cost_usd=round(self.total_tokens * 0.000002, 6),
            stage_summaries=stage_summaries,
        )

    def _configure_runtime(self) -> None:
        if not self.settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for Agents SDK mode")
        os.environ["OPENAI_API_KEY"] = self.settings.openai_api_key
        os.environ["OPENAI_BASE_URL"] = self.settings.openai_base_url
        os.environ["OPENAI_AGENTS_DISABLE_TRACING"] = (
            "0" if self.settings.agent_tracing_enabled else "1"
        )
        os.environ["OPENAI_AGENTS_TRACE_INCLUDE_SENSITIVE_DATA"] = "0"

    def _run_agent(self, agent: Any, input_text: str, output_type: type[OutputT]) -> OutputT:
        from agents import Runner

        result = Runner.run_sync(
            agent,
            input_text,
            max_turns=self.settings.agent_max_turns,
        )
        usage = getattr(getattr(result, "context_wrapper", None), "usage", None)
        self.total_tokens += int(getattr(usage, "total_tokens", 0) or 0)
        output = result.final_output
        if isinstance(output, output_type):
            return output
        if isinstance(output, str):
            return output_type.model_validate_json(output)
        return output_type.model_validate(output)

    @staticmethod
    def _json_input(**values: object) -> str:
        return json.dumps(values, ensure_ascii=False, default=str)

    @staticmethod
    def _dedupe(values: list[str]) -> list[str]:
        return list(dict.fromkeys(item for item in values if item))
