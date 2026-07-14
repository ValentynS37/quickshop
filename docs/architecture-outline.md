# BADS AI Administrator — Pilot Architecture Outline

## Static demo

- HTML/CSS/JavaScript interface;
- synthetic scenarios;
- browser-side workflow animation;
- browser-side Evidence ID and approval log.

## Paid pilot architecture

```text
Client input
  → FastAPI intake API
  → PostgreSQL workflow record
  → n8n orchestration
  → configured LLM provider
  → Evidence Agent
  → approval queue
  → one approved external integration
```

## Security boundaries

- company-controlled repository and infrastructure;
- least-privilege integration credentials;
- secrets stored outside source code;
- tenant separation;
- approved data classification;
- no production integration in the static demo;
- external side effects disabled before approval;
- append-only audit events;
- cost and usage limits per tenant.

## Build versus buy

Use existing components for orchestration, models, authentication and billing during validation. Build BADS-specific evidence, policies, approval logic, reporting and control experience.

## First integration priority

Choose one after the first client discovery:

1. Gmail draft creation, or
2. internal task creation, or
3. CRM lead creation, or
4. daily management report.

Only one integration should be implemented in the first paid pilot.
