from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

import httpx

from ..config import Settings


@dataclass(slots=True)
class AgentResult:
    lead_score: int
    risk_level: str
    confidence: float
    summary: str
    proposal: str
    backlog: list[dict[str, object]]
    flags: list[str]
    model_provider: str
    model_name: str
    estimated_cost_usd: float = 0.0
    stage_summaries: list[dict[str, object]] = field(default_factory=list)


class AgentEngine:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def process(self, *, company: str, request_text: str, data_classification: str) -> AgentResult:
        mode = self.settings.agent_orchestration
        if mode == "local" or not self.settings.openai_api_key:
            return self._process_local(company, request_text, data_classification)

        if mode == "sdk":
            try:
                return self._process_agents_sdk(company, request_text, data_classification)
            except Exception:  # noqa: BLE001 - safe fallback is intentional at provider boundary
                try:
                    fallback = self._process_responses(company, request_text, data_classification)
                    fallback.flags.append("agents_sdk_fallback_to_responses")
                    return fallback
                except (httpx.HTTPError, KeyError, ValueError, json.JSONDecodeError):
                    fallback = self._process_local(company, request_text, data_classification)
                    fallback.flags.append("openai_fallback_used")
                    return fallback

        try:
            return self._process_responses(company, request_text, data_classification)
        except (httpx.HTTPError, KeyError, ValueError, json.JSONDecodeError):
            fallback = self._process_local(company, request_text, data_classification)
            fallback.flags.append("openai_fallback_used")
            return fallback

    def _process_agents_sdk(
        self,
        company: str,
        request_text: str,
        data_classification: str,
    ) -> AgentResult:
        from .sdk_agents import AgentsWorkflow

        output = AgentsWorkflow(self.settings).run(
            company=company,
            request_text=request_text,
            data_classification=data_classification,
        )
        return AgentResult(
            lead_score=output.lead_score,
            risk_level=output.risk_level,
            confidence=output.confidence,
            summary=output.summary,
            proposal=output.proposal,
            backlog=output.backlog,
            flags=output.flags,
            model_provider="openai-agents-sdk",
            model_name=self.settings.openai_model,
            estimated_cost_usd=output.estimated_cost_usd,
            stage_summaries=output.stage_summaries,
        )

    def _process_responses(self, company: str, request_text: str, data_classification: str) -> AgentResult:
        schema = {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "lead_score": {"type": "integer", "minimum": 0, "maximum": 100},
                "risk_level": {"type": "string", "enum": ["low", "medium", "high"]},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "summary": {"type": "string"},
                "proposal": {"type": "string"},
                "backlog": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "title": {"type": "string"},
                            "acceptance": {"type": "string"},
                            "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                        },
                        "required": ["title", "acceptance", "priority"],
                    },
                },
                "flags": {"type": "array", "items": {"type": "string"}},
            },
            "required": [
                "lead_score",
                "risk_level",
                "confidence",
                "summary",
                "proposal",
                "backlog",
                "flags",
            ],
        }
        payload = {
            "model": self.settings.openai_model,
            "store": False,
            "instructions": (
                "You are the BADS AI Administrator intake system. Analyze one business automation request. "
                "Never make legal, tax, payment, employment, medical, investment, or safety-critical decisions. "
                "All external actions require human approval. Return concise Ukrainian output."
            ),
            "input": (
                f"Company: {company}\n"
                f"Data classification: {data_classification}\n"
                f"Request: {request_text}"
            ),
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "bads_intake_result",
                    "strict": True,
                    "schema": schema,
                }
            },
            "max_output_tokens": 1200,
        }
        response = httpx.post(
            f"{self.settings.openai_base_url.rstrip('/')}/responses",
            headers={
                "Authorization": f"Bearer {self.settings.openai_api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=45.0,
        )
        response.raise_for_status()
        body = response.json()
        text = self._extract_output_text(body)
        data = json.loads(text)
        usage = body.get("usage") or {}
        return AgentResult(
            lead_score=int(data["lead_score"]),
            risk_level=str(data["risk_level"]),
            confidence=float(data["confidence"]),
            summary=str(data["summary"]),
            proposal=str(data["proposal"]),
            backlog=list(data["backlog"]),
            flags=list(data["flags"]),
            model_provider="openai-responses",
            model_name=str(body.get("model") or self.settings.openai_model),
            estimated_cost_usd=self._rough_cost(usage),
        )

    @staticmethod
    def _extract_output_text(body: dict[str, Any]) -> str:
        for item in body.get("output", []):
            if item.get("type") != "message":
                continue
            for content in item.get("content", []):
                if content.get("type") == "output_text" and content.get("text"):
                    return str(content["text"])
        raise KeyError("No output_text found in OpenAI response")

    @staticmethod
    def _rough_cost(usage: dict[str, Any]) -> float:
        total_tokens = int(usage.get("total_tokens") or 0)
        return round(total_tokens * 0.000002, 6)

    def _process_local(self, company: str, request_text: str, data_classification: str) -> AgentResult:
        normalized = request_text.lower()
        word_count = len(re.findall(r"\w+", normalized))
        automation_terms = ["автомат", "заяв", "пошт", "crm", "звіт", "документ", "support", "підтрим"]
        sensitive_terms = ["оплат", "догов", "подат", "зарплат", "видал", "доступ", "персональн"]
        matched = sum(term in normalized for term in automation_terms)
        sensitive = sum(term in normalized for term in sensitive_terms)

        lead_score = min(95, 52 + matched * 7 + min(word_count // 15, 12))
        risk_level = "high" if data_classification == "restricted" else "medium" if sensitive else "low"
        confidence = min(0.95, 0.68 + matched * 0.035)
        flags: list[str] = []
        if sensitive:
            flags.append("human_review_for_sensitive_action")
        if data_classification in {"confidential", "restricted"}:
            flags.append("data_boundary_review_required")
        if word_count < 30:
            flags.append("requirements_incomplete")

        summary = (
            f"{company} потребує керованого AI-workflow для первинної обробки запитів, "
            "підготовки чернеток, створення задач і формування звітності. "
            "Зовнішні дії мають залишатися під ручним погодженням."
        )
        proposal = (
            "Запропонований пілот: один вхідний канал → структурований intake → "
            "кваліфікація → чернетка результату → Evidence Agent → human approval. "
            "Перший KPI: скорочення часу первинної обробки або частки ручних кроків."
        )
        backlog = [
            {
                "title": "Погодити один pilot workflow",
                "acceptance": "Визначені джерело, вихід, власник процесу та один KPI.",
                "priority": "high",
            },
            {
                "title": "Налаштувати intake schema",
                "acceptance": "Обов'язкові поля валідовані, відсутні дані позначаються flag.",
                "priority": "high",
            },
            {
                "title": "Увімкнути Evidence Agent",
                "acceptance": "Кожен run має Evidence ID, input/output hashes та policy version.",
                "priority": "high",
            },
            {
                "title": "Додати approval queue",
                "acceptance": "Жодна зовнішня дія не виконується до approved decision.",
                "priority": "medium",
            },
        ]
        return AgentResult(
            lead_score=lead_score,
            risk_level=risk_level,
            confidence=round(confidence, 2),
            summary=summary,
            proposal=proposal,
            backlog=backlog,
            flags=flags,
            model_provider="local",
            model_name="deterministic-fallback-v1",
        )
