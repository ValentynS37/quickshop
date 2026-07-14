# BADS AI Administrator — Demo Validation Cases

## Case 1: Automation request

Expected:
- lead score displayed;
- low risk displayed;
- proposal includes email and website intake workflow;
- Evidence ID generated;
- approval remains required.

## Case 2: Analytics request

Expected:
- medium risk displayed;
- proposal includes Excel, CRM and email sources;
- executive summary workflow shown;
- no report is externally sent.

## Case 3: Support request

Expected:
- medium risk displayed;
- approved knowledge-base boundary shown;
- complex cases are routed to a person;
- no autonomous customer reply occurs.

## Approval test

1. Run a scenario.
2. Select Approve.
3. Confirm Human Approval becomes Approved.
4. Confirm timestamped evidence row appears.
5. Confirm the UI states that no external message was actually sent.

## Revision test

1. Run a scenario.
2. Select Return for revision.
3. Confirm Human Approval becomes Revision.
4. Confirm revision evidence row appears.
5. Confirm no external action occurs.
