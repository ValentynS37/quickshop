# BADS OS v2 Backend

Working FastAPI MVP for BADS AI Administrator and TrustOS Evidence Agent.

## What works

- protected intake API;
- deterministic local agent workflow without external services;
- optional OpenAI Responses API integration;
- PostgreSQL or SQLite persistence;
- Evidence ID, input/output hashes and agent-run trail;
- human approval queue;
- evidence package export;
- dashboard summary;
- Docker deployment;
- automated tests.

## Run locally

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Open API documentation at `http://localhost:8000/docs`.

Use the API key header:

```text
X-BADS-API-Key: change-me-before-production
```

## Docker

From the repository root:

```bash
docker compose up --build
```

## First request

```bash
curl -X POST http://localhost:8000/api/v1/intake \
  -H 'Content-Type: application/json' \
  -H 'X-BADS-API-Key: change-me-before-production' \
  -d '{
    "company": "Demo Logistics Ukraine",
    "contact": "operations@example.com",
    "request_text": "We receive many requests through email and the website and need classification, response drafts, tasks, and a daily report.",
    "source_type": "web_form",
    "data_classification": "internal"
  }'
```

## OpenAI mode

Set `OPENAI_API_KEY` and optionally `OPENAI_MODEL`. The backend calls the Responses API with `store: false` and structured JSON output. If the provider call fails, the run is completed by the local deterministic fallback and receives the `openai_fallback_used` flag.

## Safety boundary

The MVP prepares drafts and evidence. It does not send external messages, make payments, change contracts, delete data, alter permissions, merge code, or deploy to production. Those actions remain outside the first pilot and require an explicit approval and a separately implemented least-privilege integration.
