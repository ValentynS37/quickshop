# BADS OS AI Agents

## Connected roles

1. **BADS Coordinator** — runs the controlled specialist sequence.
2. **Intake Agent** — structures the request, scores pilot fit, and identifies missing information.
3. **Research Agent** — designs a bounded workflow and lists data requirements and risks.
4. **Sales Agent** — prepares a reviewable pilot proposal.
5. **Project Agent** — creates implementation tasks and measurable acceptance criteria.
6. **QA Agent** — checks unsafe autonomy, unsupported claims, and missing approval gates.
7. **Evidence Agent** — explains what must be recorded before the deterministic evidence service seals the run.

## Execution modes

Set `AGENT_ORCHESTRATION` to one of:

- `sdk` — OpenAI Agents SDK multi-agent workflow. This is the default when `OPENAI_API_KEY` exists.
- `responses` — one structured Responses API call.
- `local` — deterministic fallback without an external model.

In `sdk` mode, a failed SDK run falls back to the Responses API. If that also fails, BADS uses the local deterministic workflow and records fallback flags in the evidence trail.

## Privacy defaults

- Agent tracing is disabled by default.
- Sensitive trace payload capture is disabled.
- Agent prompts do not receive the contact email.
- Agents have no email, payment, deployment, deletion, or permission-changing tools.
- Every proposed external side effect remains behind the existing human approval queue.

## Configuration

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5-mini
AGENT_ORCHESTRATION=sdk
AGENT_MAX_TURNS=6
AGENT_TRACING_ENABLED=false
```

Never commit the real API key.

## Check agent status

```bash
curl -H "X-BADS-API-Key: $BADS_API_KEY" \
  http://localhost:8000/api/v1/agents
```

## Run a workflow

```bash
curl -X POST http://localhost:8000/api/v1/intake \
  -H "Content-Type: application/json" \
  -H "X-BADS-API-Key: $BADS_API_KEY" \
  -d '{
    "company": "Demo Company",
    "contact": "operations@example.com",
    "request_text": "Потрібно класифікувати заявки, готувати чернетки та формувати щоденний звіт.",
    "source_type": "manual",
    "data_classification": "internal"
  }'
```

The response stays in `awaiting_approval`; no external action is executed.
