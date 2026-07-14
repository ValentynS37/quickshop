from __future__ import annotations

from app.config import Settings
from app.services.agent_engine import AgentEngine
from app.services.sdk_agents import AgentsWorkflow, AgentsWorkflowOutput


def test_sdk_mode_uses_multi_agent_workflow(monkeypatch) -> None:
    output = AgentsWorkflowOutput(
        lead_score=88,
        risk_level="low",
        confidence=0.91,
        summary="Structured multi-agent summary.",
        proposal="Reviewable pilot proposal.",
        backlog=[
            {"title": "Map workflow", "acceptance": "Workflow approved", "priority": "high"},
            {"title": "Configure intake", "acceptance": "Schema validated", "priority": "high"},
            {"title": "Enable evidence", "acceptance": "Evidence ID stored", "priority": "medium"},
        ],
        flags=["human_approval_required"],
        estimated_cost_usd=0.01,
        stage_summaries=[
            {
                "agent_name": "BADS Coordinator",
                "decision_summary": "Specialists completed.",
                "confidence": 0.91,
                "flags": [],
            }
        ],
    )

    def fake_run(self, **kwargs):
        return output

    monkeypatch.setattr(AgentsWorkflow, "run", fake_run)
    settings = Settings(
        bads_api_key="test-key",
        openai_api_key="test-openai-key",
        agent_orchestration="sdk",
    )
    result = AgentEngine(settings).process(
        company="Demo Company",
        request_text="We need a controlled workflow for customer request triage and reporting.",
        data_classification="internal",
    )

    assert result.model_provider == "openai-agents-sdk"
    assert result.lead_score == 88
    assert result.stage_summaries[0]["agent_name"] == "BADS Coordinator"


def test_local_mode_never_calls_sdk(monkeypatch) -> None:
    def fail_run(self, **kwargs):
        raise AssertionError("SDK must not run in local mode")

    monkeypatch.setattr(AgentsWorkflow, "run", fail_run)
    settings = Settings(
        bads_api_key="test-key",
        openai_api_key="test-openai-key",
        agent_orchestration="local",
    )
    result = AgentEngine(settings).process(
        company="Demo Company",
        request_text="Потрібно автоматизувати заявки, створення задач та щоденні звіти для керівника.",
        data_classification="internal",
    )

    assert result.model_provider == "local"
