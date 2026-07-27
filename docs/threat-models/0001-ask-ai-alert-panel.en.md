# Threat Model: Ask AI About This Alert Panel

---
feature: Ask AI about this alert panel
date: 2026-07-25
status: draft
---

## Component and Trust Boundaries

Planned feature: user clicks an alert (Sentinel/Defender/ATT&CK coverage
gap) on the Security Dashboard → a Django view collects JSON context
(coverage matrix, alert details, HTTP anomalies) → sends it to the Claude
API → the response (explanation + suggested Terraform fix) is rendered
back to the user in the browser.

Trust boundaries crossed:
1. User's browser → Django view (standard, already covered by MSAL/CIAM auth)
2. Django view → external Claude API (NEW boundary — data leaves the
   Azure perimeter)
3. Claude API response → rendering in the browser (potential XSS surface
   if the response contains unescaped HTML/markdown)
4. Suggested Terraform fix → potential further application by a human
   (NOT automated apply — a critical boundary that must remain manual)

## STRIDE Analysis

### Spoofing
Someone could forge the alert_id parameter in a request to the view,
causing the system to collect and send SOMEONE ELSE'S alert context (or
simulated cross-tenant data) to the Claude API. Mitigation: verify that
alert_id belongs to the current authenticated session/workspace; never
accept an arbitrary ID without validating it against the real Sentinel
workspace.

### Tampering
If the JSON context is assembled from multiple sources (coverage matrix +
live Sentinel alert + HTTP anomalies), someone with intermediate network/
log access could theoretically tamper with data before it reaches the
prompt. Mitigation: all collection happens server-side via already
authenticated MSI calls (Log Analytics), with no client-side proxying.

### Repudiation
There is no audit trail of which suggested fixes the AI panel has ever
generated, or whether anyone applied them. This is a direct, still-open
gap — a MUST HAVE before release: log every request (who, when, which
alert_id, what response) to a dedicated table/AppTraces entry.

### Information Disclosure — MOST CRITICAL SECTION
- Sentinel alert data (possibly including real IPs, User-Agent strings,
  usernames) leaves the Azure perimeter and goes to the external Claude
  API. This requires an explicit decision: is it acceptable to send this
  data externally, or is prior PII redaction/anonymization required?
- Risk that structured context (Terraform resource names, subnet ranges,
  subscription ID) becomes part of a request to a third-party service.
  Mitigation: minimize context to the necessary minimum; do NOT include
  raw secrets or full Terraform files — only summarized facts
  (technique_id, status, a short control/detection text).
- Knowledge leakage in the opposite direction: the AI may "guess" details
  of the architecture from its training data and present the guess as
  fact about THIS system — requires explicit tracing of every claim back
  to a specific field in the input JSON.

### Denial of Service
No rate limiting exists on the new endpoint — theoretically, anyone with
Security Dashboard access could spam requests to the Claude API, causing
unpredictable cost/latency. Mitigation: rate limit at the view level
(e.g. django-ratelimit) plus a short TTL cache for identical alert_ids.

### Elevation of Privilege
The most critical requirement: the MSI/service performing this call must
have STRICTLY read-only access to the Log Analytics/Sentinel API. The
suggested Terraform fix must NEVER be automatically applied (`terraform
apply`) without an explicit, separate, manual human action — the Claude
API here only generates recommendation TEXT, it never executes any
infrastructure changes. A verification step (confirming that any
Terraform resources mentioned in the suggestion actually exist in the
current state) must run BEFORE the response is shown to the user, not
after.

## Identified Action Items

- [ ] Validate alert_id against the real workspace before collecting context
- [ ] Audit-log every AI request (who/when/what) → relates to A.8.15 Logging
- [ ] Explicit decision on PII redaction in context before sending to the Claude API
- [ ] Rate limiting on the endpoint
- [ ] Verify mentioned Terraform resources against the real state before showing the recommendation
- [ ] Explicit MSI role: read-only only (Log Analytics Reader, Security Reader) — NEVER write/Contributor
- [ ] Explicit citation of the source (which JSON field) for every claim in the AI's response

## Related Records

- Compliance: A.8.15/A.8.16 Logging & Monitoring (docs/compliance/0015, 0016)
- Compliance: A.8.24 Use of Cryptography
- Backlog record #7 (project memory, 24.07.2026): knowledge-graph context
  + knowledge-leakage safeguards
