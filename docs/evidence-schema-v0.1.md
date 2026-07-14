# BADS Evidence Agent — Schema v0.1

## Goal

Create a verifiable record of every AI-assisted workflow run without exposing unnecessary personal or confidential data.

## Evidence package

```json
{
  "evidence_id": "BADS-YYYYMMDD-0001",
  "workflow_id": "ai-admin-intake-v1",
  "workflow_version": "0.1.0",
  "created_at": "ISO-8601 timestamp",
  "tenant_id": "client identifier",
  "input": {
    "source_type": "web_form | email | api | manual",
    "source_reference": "internal reference",
    "content_hash": "sha256",
    "received_at": "ISO-8601 timestamp",
    "data_classification": "public | internal | confidential | restricted"
  },
  "agent_runs": [
    {
      "agent_name": "Intake Agent",
      "agent_version": "0.1.0",
      "model_provider": "configured provider",
      "model_name": "configured model",
      "prompt_policy_version": "policy identifier",
      "started_at": "ISO-8601 timestamp",
      "completed_at": "ISO-8601 timestamp",
      "input_hash": "sha256",
      "output_hash": "sha256",
      "decision_summary": "short non-sensitive explanation",
      "confidence": 0.0,
      "flags": [],
      "tool_calls": [],
      "estimated_cost": 0.0
    }
  ],
  "proposed_action": {
    "type": "draft_email | create_task | update_crm | generate_report",
    "target": "internal target reference",
    "risk_level": "low | medium | high",
    "external_side_effect": false
  },
  "approval": {
    "required": true,
    "status": "pending | approved | rejected | expired",
    "reviewer_id": null,
    "reviewed_at": null,
    "review_note": null
  },
  "outcome": {
    "status": "drafted | blocked | executed | failed",
    "executed_at": null,
    "result_hash": null,
    "error_code": null
  },
  "integrity": {
    "package_hash": "sha256",
    "previous_evidence_hash": null,
    "retention_policy": "policy identifier"
  }
}
```

## Required rules

1. Every input receives an Evidence ID before agent processing.
2. Raw secrets, access tokens and passwords are never stored in evidence records.
3. Sensitive content is referenced by hashes and controlled storage locations where possible.
4. Every agent run records its version, policy version and output hash.
5. Any external side effect requires an explicit risk classification.
6. Email sending, financial actions, contract changes, deletion, production deployment and permission changes always require human approval.
7. Rejected and blocked actions remain visible in the audit trail.
8. Evidence records are append-only after sealing; corrections create a linked successor record.
9. Tenant data must be logically separated.
10. The first pilot uses synthetic or explicitly approved data only.

## Human approval policy

### Automatic drafting allowed

- classify an inbound request;
- summarize approved content;
- prepare a reply draft;
- propose tasks;
- prepare an internal report;
- calculate non-binding lead scores.

### Human approval mandatory

- send an external message;
- create or modify a contract;
- make or request payment;
- change access permissions;
- delete or overwrite data;
- publish content;
- merge code or deploy to production;
- make legal, tax, employment, medical or investment decisions.

## Minimum dashboard fields

- Evidence ID;
- workflow and version;
- source type;
- created time;
- lead or confidence score;
- risk level;
- agent timeline;
- anomaly flags;
- proposed action;
- approval status;
- final outcome;
- export button.

## Pilot acceptance criteria

- 100% of demo runs create an Evidence ID;
- 100% of external actions are blocked before approval;
- every output has an input and output hash;
- every decision displays a short explanation;
- approval and rejection are recorded with timestamp;
- no credentials appear in logs or exports.
