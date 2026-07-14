# BADS AI Administrator — Executable Technical Backlog

## Sprint 0 — pilot readiness

### AAI-001: Merge and deploy the static demo

**Acceptance criteria**
- `ai-admin.html` opens from the deployed branch preview;
- all three synthetic scenarios run;
- approve and revision actions are recorded in the evidence trail;
- mobile layout remains usable;
- the page clearly states that it performs no external actions.

### AAI-002: Select the first pilot workflow

**Acceptance criteria**
- one client and one process selected;
- one primary KPI selected;
- data classification recorded;
- prohibited autonomous actions documented;
- pilot owner and approver named;
- written permission obtained for any real client data.

## Sprint 1 — backend foundation

### AAI-101: FastAPI service

**Deliverables**
- health endpoint;
- versioned `/api/v1/intake` endpoint;
- request validation;
- structured error responses;
- environment-based configuration;
- automated tests.

### AAI-102: PostgreSQL persistence

**Core tables**
- tenants;
- users;
- workflows;
- workflow_runs;
- agent_runs;
- evidence_packages;
- approvals;
- actions;
- audit_events.

**Acceptance criteria**
- tenant separation enforced;
- timestamps stored in UTC;
- sensitive values excluded from logs;
- schema migrations included.

### AAI-103: Evidence ID and hashing

**Acceptance criteria**
- Evidence ID created before processing;
- input and output SHA-256 hashes stored;
- policy and workflow versions recorded;
- evidence package can be exported as JSON;
- sealed evidence records cannot be silently overwritten.

## Sprint 2 — agent workflow

### AAI-201: Intake Agent

**Acceptance criteria**
- extracts organization, contact, request, urgency and missing fields;
- stores structured output;
- confidence and flags included;
- unsupported content routed to human review.

### AAI-202: Qualification Agent

**Acceptance criteria**
- uses an approved scoring policy;
- produces fit, risk and recommended next step;
- gives a short explanation;
- cannot reject or contact a client autonomously.

### AAI-203: Proposal Agent

**Acceptance criteria**
- uses an approved commercial template;
- distinguishes founding, standard and custom pilot offers;
- includes exclusions and assumptions;
- output remains a draft.

### AAI-204: Project Agent

**Acceptance criteria**
- generates milestones, tasks and acceptance criteria;
- identifies required integrations;
- identifies data and security dependencies;
- creates no external issue or calendar event without approval.

### AAI-205: Evidence Agent

**Acceptance criteria**
- implements `docs/evidence-schema-v0.1.md`;
- records every agent run;
- records model, policy version, tool calls and cost estimate;
- blocks completion if required evidence fields are missing.

## Sprint 3 — approval and first integration

### AAI-301: Human approval queue

**Acceptance criteria**
- pending actions displayed in one queue;
- approve, reject and request revision supported;
- reviewer and timestamp recorded;
- expired approvals cannot execute;
- high-risk actions always require approval.

### AAI-302: One pilot integration

Choose only one for the first pilot:
- Gmail draft creation;
- CRM lead creation;
- internal task creation;
- daily email report.

**Acceptance criteria**
- least-privilege credentials;
- sandbox or test workspace first;
- idempotency protection;
- retry and failure logging;
- external action disabled until approval.

## Sprint 4 — commercialization

### AAI-401: Pilot KPI dashboard

- volume processed;
- median processing time;
- classification accuracy sample;
- drafts accepted and revised;
- manual steps removed;
- model/API cost;
- exceptions requiring human review.

### AAI-402: Client onboarding template

- service scope;
- data map;
- roles and approval matrix;
- knowledge-base approval;
- retention policy;
- escalation contacts;
- pilot KPI and baseline;
- case-study permission.

### AAI-403: Subscription control panel

Build only after at least three pilots demonstrate repeated demand.

Minimum scope:
- tenant login;
- workflows;
- usage and limits;
- evidence search;
- approval queue;
- billing status;
- support requests.

## Definition of done for the first paid pilot

- one real business process runs end to end;
- no prohibited autonomous actions;
- every run has an Evidence ID;
- the agreed KPI is measured before and after;
- client signs off on results;
- reusable template extracted;
- monthly managed-service offer presented.
