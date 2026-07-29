# Spec: Ask AI About This Alert Panel

**Status:** Draft
**Feature ID:** `SEC-DASH-ASKAI-01`
**Related backlog item:** 21.07.2026 (original idea), refined 24.07.2026 (citation/verification safeguards), STRIDE threat-modeled 25.07.2026 (`docs/threat-models/0001-ask-ai-alert-panel.md`), formalized into this EARS spec 28.07.2026 after the threat model was discovered during a verification pass
**Owner:** Vitalii Shevchuk
**Target surface:** new Django view (e.g. `security_ask_ai` in `core/views.py`), new template partial, external Claude API integration, `attack_data.json` / Sentinel alert data as input context

---

## 1. Overview

Add a panel to the Security Dashboard where a user clicks an alert (Sentinel/Defender/ATT&CK coverage gap) and receives an AI-generated explanation plus a suggested Terraform fix, rendered as read-only text. This spec is **not new analysis** — it is a direct translation of an already-complete STRIDE threat model (`docs/threat-models/0001-ask-ai-alert-panel.md`, dated 25.07.2026) into EARS requirements. Every REQ below traces to a specific STRIDE finding in that document; none are invented for this spec.

**This is a code change requiring both docs-only work (view logic, prompt construction) and one Azure touch (a Key Vault secret for the Claude API key, if not already available via an existing integration) — see NFR-01.**

## 2. Problem Statement

The Security Dashboard currently shows raw coverage/alert data (ATT&CK matrix, Defender alerts, HTTP anomalies) with no interpretive layer — a user must manually correlate a `gap`-status technique or a live alert with what to actually do about it. The threat model identified this as valuable but flagged five real, unresolved risk categories (Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege, plus Spoofing/Tampering) that must be addressed in the implementation, not discovered after shipping.

## 3. Scope

**In scope:**
- A new view that accepts an `alert_id` (or `technique_id`), assembles a minimized JSON context, sends it to the Claude API, and renders the response
- All STRIDE mitigations identified in the threat model, translated into explicit, testable requirements
- Audit logging of every request

**Out of scope (explicitly deferred — per the threat model's Elevation of Privilege finding, this is a hard boundary, not a future increment):**
- Automatic application of any suggested Terraform fix (`terraform apply`) — the panel only ever produces text for a human to review and apply manually
- Multi-turn conversation or chat-style follow-up — single request, single response only, to keep the trust boundary and cost surface small
- Any write-capable MSI role or credential for this feature — it must remain read-only, permanently (see REQ-09)

## 4. Data Model

**Context sent to the Claude API** (per the threat model's Information Disclosure mitigation — minimized, not raw):

```json
{
  "alert_id": "...",
  "technique_id": "T1595",
  "status": "gap",
  "control_summary": "No WAF or IP restriction rules configured",
  "detection_summary": "Defender for App Service detected NMap (T1595.001)",
  "http_anomaly_summary": "5 requests, scanner-tool user agent detected"
}
```

Explicitly **excluded** from this context: raw Terraform file contents, full secret values, full Terraform state, and (pending Open Question 1 below) raw IP addresses / usernames / User-Agent strings from the underlying Sentinel data unless a redaction decision explicitly allows them.

**Audit log entry** (per the Repudiation finding — a MUST HAVE, not optional):

```json
{
  "timestamp": "...",
  "user": "...",
  "alert_id_or_technique_id": "...",
  "context_sent": { "...": "..." },
  "response_received": "...",
  "terraform_resources_mentioned": ["..."],
  "verification_result": "all resources confirmed to exist in state | discrepancy found: ..."
}
```

## 5. Requirements (EARS notation)

### 5.1 Input validation and data integrity (Spoofing / Tampering)

- **REQ-01 (Unwanted behavior):** If a request's `alert_id` does not belong to the current authenticated session's Sentinel workspace, then the view shall reject the request rather than collecting or forwarding any context.
- **REQ-02 (Ubiquitous):** All context collection (coverage matrix, alert details, HTTP anomalies) shall happen server-side via the already-authenticated MSI calls already used elsewhere in the Security Dashboard — no client-side proxying or client-supplied context fields shall be trusted.

### 5.2 Information disclosure minimization (most critical STRIDE category)

- **REQ-03 (Ubiquitous):** The JSON context sent to the Claude API shall be limited to the minimized shape in section 4 — `technique_id`, `status`, and short summary text — and shall never include raw Terraform file contents, full secret values, or full Terraform state.
- **REQ-04 (Ubiquitous):** Every factual claim in the AI's rendered response shall be traceable to a specific field in the input JSON context; the response rendering shall make this traceability visible (e.g., inline citation of which field a claim derives from), not merely assumed.
- **REQ-05 (Unwanted behavior):** If the AI's response mentions a Terraform resource name, then the system shall verify that resource actually exists in the current Terraform state **before** displaying the response to the user, and shall flag any mismatch rather than silently showing an unverified claim.

### 5.3 Repudiation — audit trail (MUST HAVE per threat model)

- **REQ-06 (Ubiquitous):** Every request to this panel shall be logged (user, timestamp, alert/technique ID, context sent, response received, verification result) per the shape in section 4, before the response is returned to the user.

### 5.4 Denial of service / cost control

- **REQ-07 (Ubiquitous):** The view shall be rate-limited per user/session (e.g., via `django-ratelimit`) to prevent unbounded Claude API cost or latency from repeated requests.
- **REQ-08 (State-driven):** While a cached response exists for a given `alert_id` within its TTL window, the system shall serve the cached response rather than issuing a new Claude API call.

### 5.5 Elevation of privilege (most critical STRIDE category, permanent constraint)

- **REQ-09 (Ubiquitous):** The MSI/service identity used to collect context for this feature shall hold strictly read-only roles (Log Analytics Reader, Security Reader) — the same roles already granted for the rest of the Security Dashboard — and shall never be granted Contributor or any write-capable role, permanently, not just at initial implementation.
- **REQ-10 (Unwanted behavior):** If a suggested Terraform fix is generated, then the system shall render it as read-only text only — under no circumstance shall this feature execute `terraform apply` or any other infrastructure-modifying action automatically.

## 6. Non-Functional Requirements

- **NFR-01:** Requires one Azure touch — a Key Vault secret for the Claude API key (if not already available via an existing integration elsewhere in the project) — following the existing Key Vault secrets pattern. No new Azure compute, networking, or additional MSI roles beyond what's already granted for the Security Dashboard (REQ-09 reuses existing roles).
- **NFR-02:** Cost awareness — per the "harness engineering" budget-limit principle (Yazidi, "From Prompt to Production"; Loop vs. Harness Engineering discussion, this session), REQ-07/REQ-08 (rate limiting + caching) exist specifically to bound Claude API cost exposure, not only to reduce latency. Any future iteration should track actual per-request cost, not assume it's negligible.
- **NFR-03:** No multi-turn state, no background job, no autonomous loop — this is a single request/response feature (see Scope). The "harness vs. loop engineering" distinction (this session's article review) does not apply here in its full form, since there is no autonomous loop to guard — but the read-only/no-auto-apply constraints (REQ-09, REQ-10) are still harness-engineering guardrails in the sense of that discussion.

## 7. Task Breakdown

**Why this section exists:** batching requirements avoids handing an AI coding agent a dozen-plus requirements in one shot, which risks context rot (see `docs/specs/TEMPLATE.md` section 7). Each batch below is sized for a single fresh Claude Code session.

| Batch | REQs covered | Description | Depends on | Azure write required? |
|---|---|---|---|---|
| 1 | REQ-01, REQ-02, REQ-09 | Core view skeleton: input validation, server-side context collection reusing existing MSI roles | - | No (reuses existing role, no new grant) |
| 2 | REQ-03, REQ-04, REQ-05 | Context minimization, citation-traceable rendering, Terraform-state verification step | Batch 1 | No |
| 3 | REQ-06 | Audit logging | Batch 1 | No |
| 4 | REQ-07, REQ-08, REQ-10 | Rate limiting, caching, hard guardrail against auto-apply | Batch 1, 2 | Mixed — REQ-10 itself needs no Azure write access (it's a guardrail preventing one), but the Key Vault secret for the Claude API key (NFR-01) should be provisioned before this batch is tested end-to-end |

## 8. Acceptance Criteria (checklist)

Directly mirrors the threat model's own "Identified Action Items" list — nothing added, nothing dropped:

- [ ] Validate `alert_id` against the real workspace before collecting context (REQ-01)
- [ ] Audit-log every AI request (who/when/what) — relates to A.8.15 Logging (REQ-06)
- [ ] Explicit decision made on PII redaction in context before sending to the Claude API (REQ-03 + Open Question 1)
- [ ] Rate limiting on the endpoint (REQ-07)
- [ ] Verify mentioned Terraform resources against the real state before showing the recommendation (REQ-05)
- [ ] Explicit MSI role: read-only only (Log Analytics Reader, Security Reader) — never write/Contributor (REQ-09)
- [ ] Explicit citation of the source (which JSON field) for every claim in the AI's response (REQ-04)

## 9. Open Questions

1. **PII redaction policy — the threat model itself flags this as requiring "an explicit decision" but does not make one.** Should raw IPs, User-Agent strings, or usernames from Sentinel alert data ever be included in the context sent to the external Claude API? **Recommendation:** default to **not** including them — the minimized context in section 4 (technique_id, status, short summaries) is sufficient for the panel's stated purpose (explain a gap, suggest a fix), and raw identifiers add disclosure risk without clear corresponding value. Revisit only if a specific, well-justified use case requires them, and treat that as a separate, explicitly-approved exception — not a default.
2. Which concrete integration mechanism to use for the Claude API call (direct Anthropic SDK call from Django, vs. some other pattern) is not yet decided. **Needs decision:** before Batch 1 implementation, confirm the simplest viable approach (likely a direct API call using the project's existing Python/Django stack, with the API key sourced from Key Vault per NFR-01).

## 10. Traceability

This spec's sole source of truth for *what* to require is `docs/threat-models/0001-ask-ai-alert-panel.md` — if that threat model is ever revised, this spec must be re-checked for consistency (and vice versa; do not let the two drift independently). It also references the existing compliance records `docs/compliance/0015-a-8-15-logging.md` and `docs/compliance/0016-a-8-16-monitoring-activities.md` for REQ-06's audit-logging requirement, and is stylistically consistent with the citation/verification discipline already established in `evidence-linked-attack-mapping.spec.md` (traceable claims, explicit sourcing) — though it shares no data model with that spec. Independent of the other 6 specs in `docs/specs/README.md` for implementation purposes.

## Revision Log

| Date | Change | Reason |
|---|---|---|
| 28.07.2026 | Initial draft created, translating the complete STRIDE threat model (`docs/threat-models/0001-ask-ai-alert-panel.md`, 25.07.2026) into EARS requirements | Discovered during the Security Dashboard baseline spec's verification pass that a full threat model already existed for this backlog item but had never been formalized into an implementable spec |