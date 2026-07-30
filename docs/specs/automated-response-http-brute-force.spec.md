# Spec: Automated Response — HTTP Brute Force Session Revocation

**Status:** Draft
**Feature ID:** `SEC-SENTINEL-AUTORESPONSE-01`
**Related backlog item:** Automated response gap, open since 24.07.2026 ("no Sentinel rule currently has an attached playbook/automated response") — formalized into this EARS spec 28.07.2026, sourced from the already-drafted `docs/playbooks/T1110-http-brute-force.md`
**Owner:** Vitalii Shevchuk
**Target surface:** new Azure Logic App + Terraform module, Sentinel automation rule binding, Microsoft Graph API (`revokeSignInSessions`), `docs/playbooks/T1110-http-brute-force.md` (to be updated once implemented)

---

## 1. Overview

Build a Logic App playbook that automatically revokes sign-in sessions for an account confirmed compromised by the existing `HTTP Brute Force - Repeated Auth Failures on /auth/login/` Sentinel rule — closing a gap this project has tracked since 24.07.2026 and that the playbook itself already names as its own missing piece. This spec's content is sourced entirely from the existing playbook's Eradication and Communication sections, translated into EARS requirements, with one addition not present in the source playbook: an explicit idempotency requirement, motivated by this session's review of Mouez Yazidi's "From Prompt to Production" article — a real-world side-effect action (session revocation) must be safe to trigger more than once for the same incident before it is given any autonomy.

## 2. Problem Statement

`docs/playbooks/T1110-http-brute-force.md`'s Eradication section states, verbatim in intent: if a specific account was targeted successfully, force session revocation for that account — currently manual, automated `revokeSignInSessions` playbook not yet implemented. This has been an open, named backlog item for over a month. Per this project's own `CONSTITUTION.md` (Terraform & Infrastructure Changes, Rule #2), any automated action with a real-world side effect needs the same category of hard guardrail already established for AI-suggested Terraform changes — the difference here is the guardrail is idempotency and permission scoping, not "never auto-apply," since this action's whole purpose is to execute automatically once a clear, narrow trigger condition is met.

## 3. Scope

**In scope:**
- A Logic App triggered by a Sentinel automation rule bound to the existing `HTTP Brute Force - Repeated Auth Failures on /auth/login/` analytics rule
- Triggering only on the playbook's own defined escalation condition — a successful (2xx) login from the same source IP following a failure cluster — not on every brute-force alert
- Idempotency handling so the same Sentinel incident + account pair is never processed twice
- Narrowly-scoped Microsoft Graph permission for the Logic App's identity
- Audit logging of every execution (successful, skipped-as-duplicate, or failed)
- Updating the source playbook's Eradication checklist once this is implemented and verified

**Out of scope (explicitly deferred):**
- Automating containment for the T1595 WAF gap — separate, already-tracked backlog item, unrelated trigger condition
- Automated response for the distributed password-spray detection rule (not yet built, per the 24.07.2026 backlog item) — this spec covers only the existing single-IP brute-force rule
- A general-purpose, reusable automated-response framework for arbitrary future Sentinel rules — per `CONSTITUTION.md`'s Scope Discipline rule, build for this one confirmed use case now; generalize only once a second real use case exists
- Auto-revoking sessions on failure-cluster detection alone, without a subsequent successful login — the playbook is explicit that this case is "log only, no escalation"

## 4. Data Model

**Idempotency tracking record** (one per processed incident+account pair):

```json
{
  "idempotency_key": "<sentinel_incident_id>:<account_upn>",
  "sentinel_incident_id": "...",
  "account_upn": "...",
  "action": "revokeSignInSessions",
  "status": "success | already_processed | failed | in_progress",
  "timestamp": "...",
  "source_ip": "..."
}
```

The idempotency key is the combination of the Sentinel incident ID and the target account's UPN — not just the incident ID alone, in case a single incident somehow implicates more than one account, and not just the account alone, since the same account could legitimately be targeted again by a genuinely new, later incident.

## 5. Requirements (EARS notation)

### 5.1 Trigger condition (matching the playbook's own escalation criterion)

- **REQ-01 (Event-driven):** When the `HTTP Brute Force - Repeated Auth Failures on /auth/login/` Sentinel rule fires **and** a subsequent successful (2xx) login is detected from the same source IP within the same incident window, the system shall trigger the automated response Logic App.
- **REQ-02 (Unwanted behavior):** If the brute-force rule fires without any subsequent successful login from the offending IP, then the system shall **not** trigger automated session revocation — per the playbook's own "single IP, <50 failures, no successful login: log only, no escalation" criterion.

### 5.2 Idempotency (the Yazidi-article addition — not present in the source playbook)

- **REQ-03 (Ubiquitous):** Every automated response execution shall use an idempotency key derived from the Sentinel incident ID and the target account UPN, per the Data Model in section 4.
- **REQ-04 (Unwanted behavior):** If a revocation request is received for an idempotency key already marked `success` or `already_processed`, then the system shall skip the Graph API call entirely and log the attempt as `already_processed` — never issue a duplicate `revokeSignInSessions` call for the same incident+account pair.
- **REQ-05 (State-driven):** While a revocation request for a given idempotency key is marked `in_progress`, the system shall reject or queue (never concurrently execute) any duplicate request for the same key — guarding against a race condition if the Logic App is triggered twice in quick succession for the same incident.

### 5.3 Permission scoping (permanent guardrail, per `CONSTITUTION.md`)

- **REQ-06 (Ubiquitous):** The Logic App's execution identity shall hold only the minimum Microsoft Graph application permission required to call `revokeSignInSessions` — never a broader Graph permission grant "for convenience."
- **REQ-07 (Unwanted behavior):** If the Logic App's identity is ever granted a broader permission than REQ-06 specifies, then this shall be treated as a `CONSTITUTION.md`-class violation requiring immediate remediation — logged as a new entry in that file's incident history, not silently accepted.

### 5.4 Audit trail

- **REQ-08 (Ubiquitous):** Every automated response execution — successful, skipped-as-duplicate, or failed — shall be logged with incident ID, account UPN, action taken, timestamp, and status, following the same audit-trail principle already established for the Ask AI Alert Panel spec's REQ-06.

### 5.5 Playbook synchronization

- **REQ-09 (Event-driven):** When this automation is implemented and verified working end-to-end, the author shall update `docs/playbooks/T1110-http-brute-force.md`'s Eradication section to reflect that automated revocation now exists, replacing its current "manual process only" note — per this project's established discipline against letting related documents silently drift out of sync.

## 6. Non-Functional Requirements

- **NFR-01:** Requires new Azure resources — a Logic App, a Sentinel automation rule binding, and a Microsoft Graph application permission grant. This is Azure write access, currently blocked by the subscription billing issue.
- **NFR-02:** Cost — Logic App consumption-based pricing, expected to be low given the rule's low historical trigger frequency (a handful of real incidents to date). Once implemented, this is a good first candidate to actually exercise the Security Investment Cost-Effectiveness Model (Spec #8) against a real, small action rather than only a hypothetical one.
- **NFR-03:** This is a single-trigger, single-action response — not a multi-step autonomous reasoning loop. Per this session's Loop vs. Harness Engineering discussion, only the "harness" concerns (idempotency, permission scoping) apply here; there is no scheduling/stopping "loop" to design.

## 7. Task Breakdown

| Batch | REQs covered | Description | Depends on | Azure write required? |
|---|---|---|---|---|
| 1 | REQ-01, REQ-02 | Sentinel automation rule binding + trigger-condition logic (successful login after failure cluster) | - | Yes |
| 2 | REQ-03, REQ-04, REQ-05 | Idempotency tracking (likely a lightweight Azure Table Storage table, given low expected volume) | Batch 1 | Yes |
| 3 | REQ-06, REQ-07 | Microsoft Graph permission scoping via Terraform | Batch 1 | Yes |
| 4 | REQ-08 | Audit logging, reusing the existing Log Analytics / AppTraces pattern where possible | Batch 1, 2 | Yes |
| 5 | REQ-09 | Update the source playbook's Eradication section | Batch 1-4 complete and verified | No |

## 8. Acceptance Criteria (checklist)

- [ ] Logic App triggers only on the escalation condition (successful login after failure cluster), never on failure-cluster-alone (REQ-01, REQ-02)
- [ ] Idempotency key correctly derived and checked before every Graph API call (REQ-03, REQ-04)
- [ ] Concurrent/duplicate triggers for the same incident+account do not cause concurrent revocation calls (REQ-05)
- [ ] Logic App identity holds only the minimum required Graph permission — verified directly, not assumed (REQ-06)
- [ ] Every execution outcome (success/already_processed/failed) is logged with full context (REQ-08)
- [ ] `docs/playbooks/T1110-http-brute-force.md` updated to reflect the new automated capability once verified working (REQ-09)

## 9. Open Questions

1. What storage mechanism should back the idempotency tracking table? **Recommendation:** a lightweight Azure Table Storage table — given very low expected trigger volume (a handful of real incidents historically), provisioning a full database (Cosmos DB, PostgreSQL) would be disproportionate per `CONSTITUTION.md`'s Scope Discipline rule. Revisit only if actual volume proves this insufficient.
2. Should this Logic App's pattern be generalized into a reusable template for future automated responses (e.g., once the distributed password-spray rule exists)? **Recommendation:** no, not yet — build single-purpose for this one confirmed use case now; generalize only when a second real use case exists, per the same Scope Discipline rule.

## 10. Traceability

This spec's sole content source is `docs/playbooks/T1110-http-brute-force.md` (Eradication and Communication sections) — if that playbook is ever revised, this spec must be re-checked for consistency, and vice versa. It applies `CONSTITUTION.md`'s Rule #1 (Azure Identity & Secrets) and Rule #2 (Terraform & Infrastructure Changes) principles to a new context (automated response permission scoping) and follows the audit-trail pattern already established in `ask-ai-alert-panel.spec.md`'s REQ-06. It is a candidate first real application of `security-investment-cost-effectiveness-model.spec.md` (Spec #8) once implemented. Independent of Groups A and C in `docs/specs/README.md` — belongs in Group B alongside the IOC Reputation Lookup and SECURITY.md Honest Limitations specs.

## Revision Log

| Date | Change | Reason |
|---|---|---|
| 28.07.2026 | Initial draft created, translating `docs/playbooks/T1110-http-brute-force.md`'s Eradication/Communication sections into EARS requirements, with idempotency (REQ-03/04/05) added as new content not present in the source playbook | Closes a backlog item open since 24.07.2026; idempotency requirement directly motivated by this session's review of Yazidi's "From Prompt to Production" article |

---

## Requirement Traceability Verification (fill in only after implementation)

**Do not populate this section while authoring the spec.** Prompt to use for this pass:

> Audit the completed Logic App implementation against `docs/specs/automated-response-http-brute-force.spec.md`. For every requirement REQ-01 through REQ-09, provide: Status (satisfied / partially satisfied / missing), implementation file/resource, test/verification evidence.

| REQ | Status | Implementation (file:symbol) | Test/Verification | Notes |
|---|---|---|---|---|
| REQ-01 | — | — | — | — |
| REQ-02 | — | — | — | — |

Only change this spec's **Status** field from `Draft` to `Implemented` once this table is fully populated and every requirement is `satisfied`.