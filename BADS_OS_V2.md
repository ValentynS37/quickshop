# BADS OS v2

This iteration turns the static BADS AI Administrator demo into a working backend MVP.

## Implemented

- FastAPI service;
- SQLite development mode and PostgreSQL Docker mode;
- API-key protection;
- Intake, Qualification, Proposal, Project and Evidence agent records;
- deterministic offline fallback;
- optional OpenAI Responses API integration;
- Evidence ID, SHA-256 integrity hashes and exportable evidence package;
- human approval queue;
- dashboard summary endpoint;
- Docker Compose;
- CI and automated tests.

## Deliberately not implemented yet

- real email sending;
- Gmail or CRM write access;
- billing;
- multi-user authentication;
- confidential production data;
- autonomous external actions.

## Pilot gate

The first external integration is added only after one pilot client confirms one workflow, one KPI, data boundaries and an approval owner.
