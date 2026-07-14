# BADS TrustOS — Static Prototype

A product prototype for **Stoliarchuk R&D Ukraine**.

This branch contains the BADS TrustOS landing page, Command View dashboard and a commercial BADS AI Administrator pilot demo.

## Files

```text
index.html                         Ukrainian landing page
en.html                            English landing page
dashboard.html                     Static Command View demo
ai-admin.html                      AI Administrator commercial pilot demo
assets/css/bads.css                Design system and layout
assets/js/bads.js                  Landing interactions
assets/js/dashboard.js             Command View data and evidence modal
assets/js/ai-admin.js              Agent workflow, approval and evidence demo
docs/product-strategy.md           Product strategy and safe MVP scope
docs/ai-admin-pilot-launch.md      Pilot offer, targets, pricing and conversion plan
docs/evidence-schema-v0.1.md       Evidence Agent data model and approval policy
```

## Product positioning

BADS TrustOS is an **AI Trust Layer / Evidence Engine**.

It turns chaotic inputs such as photos, video, OSINT, telemetry, coordinates, documents and AI outputs into verified, explainable and actionable evidence packages.

BADS AI Administrator demonstrates the same TrustOS principles in a commercial business workflow:

```text
Inbound request
→ qualification
→ proposal draft
→ project backlog
→ evidence package
→ human approval
```

## Safe product disclaimer

BADS TrustOS is positioned as a human-in-the-loop AI trust layer, data integrity system, civil resilience tool, evidence engine and infrastructure risk analytics platform.

It does **not** provide autonomous target selection, weapon control or harmful technical implementation.

The AI Administrator demo does not send messages, spend money, sign documents, delete data or modify external systems.

## How to preview locally

Open one of the following files:

```text
index.html

dashboard.html

ai-admin.html
```

## Cloudflare Pages

This is a static site. It can be deployed directly from the repository root.

Suggested Cloudflare settings:

```text
Build command: none
Output directory: /
Root directory: /
```

## Current status

The commercial demo is interactive but still static. It uses synthetic data and browser-side logic.

Not implemented yet:

- backend API;
- database;
- authentication and tenant separation;
- real model calls;
- n8n or Dify orchestration;
- email, CRM or calendar integrations;
- append-only evidence storage;
- billing and subscription management.

## Next technical stage

1. FastAPI backend and PostgreSQL.
2. Intake endpoint and workflow persistence.
3. Agent orchestration with strict tool permissions.
4. Evidence schema implementation.
5. Human approval queue.
6. One approved pilot integration.
7. KPI and pilot-results dashboard.
8. Multi-tenant control panel and subscription billing.
