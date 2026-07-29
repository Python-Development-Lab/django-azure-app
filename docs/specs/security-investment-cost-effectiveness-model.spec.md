# Spec: Security Investment Cost-Effectiveness Model

**Status:** Draft
**Feature ID:** `SEC-RND-COSTMODEL-01`
**Related backlog item:** New R&D direction identified 28.07.2026, directly motivated by a real correction made the same day (see Problem Statement)
**Owner:** Vitalii Shevchuk
**Target surface:** new methodology document + lightweight analysis script (`docs/research/` or similar) — **not** a Security Dashboard UI feature in this iteration (see Scope)

---

## 1. Overview

Formalize a repeatable methodology for correlating this project's Azure spending data (FinOps Dashboard, `_all_cost_data()`) with Microsoft Defender for Cloud Secure Score impact, producing a defensible cost-effectiveness ranking of candidate security remediation actions. This is explicitly a **research/methodology deliverable**, not a new dashboard feature — the goal is a correct, verifiable analysis, not a live UI panel (that remains a possible future increment, out of scope here).

## 2. Problem Statement

Earlier the same day this spec was proposed, an unverified claim was made: that updating the outdated `cryptography` package would raise this project's Secure Score from 36% to ~67%, based on matching the "Remediate vulnerabilities" category (0/6 points, the single largest weighted gap) to the already-known `cryptography` CVEs. Direct verification (`az rest` against the live `Microsoft.Security/assessments` API) showed this was likely wrong: **all 8 unhealthy vulnerability assessments in that category belong to `hornetdashboardprod`**, a different project in the same Azure subscription — not to `django-azure-app`. No assumption-free confirmation exists yet that fixing `cryptography` in this project affects that Secure Score category at all.

This is concrete, first-hand evidence that intuitive cost↔security correlation claims — even ones that feel obviously true — can be wrong when a subscription contains multiple projects sharing the same Secure Score. A formal methodology, with resource-level verification built in as a hard requirement (not an afterthought), is needed before any further cost-effectiveness claims are made for this project.

## 3. Scope

**In scope:**
- A verification-first methodology for attributing Secure Score point gaps to specific, confirmed resources belonging to `django-azure-app` (not the subscription as a whole)
- A cost-estimation approach combining recurring Azure spend (FinOps data) and one-time implementation effort (hours), kept as separate, explicitly-sourced figures
- A ranking method (cost-effectiveness ratio) applied to this project's own known candidate remediation actions (WAF/Application Gateway, RBAC scope-down, `cryptography` update, PostgreSQL least-privilege role migration)
- Correcting, as this spec's first real output, the specific 36%→67% claim that motivated this spec

**Out of scope (explicitly deferred):**
- A live Security Dashboard UI panel visualizing this model — this remains a candidate for Security Dashboard Phase 2, not this iteration; this spec produces a periodic, manually-run report, not a real-time feature
- Automated/scheduled recalculation via a background job — re-running the analysis is a deliberate, occasional action (e.g., before a priority review), not continuous monitoring
- Extending the analysis to `hornetdashboardprod` or any other project in the subscription — stay strictly scoped to resources verifiably belonging to `django-azure-app`
- Formal academic publication of the methodology — the output may seed one later, but that is not this spec's deliverable

## 4. Data Model

**Remediation action record** (one per candidate action, e.g. "Update `cryptography` package"):

```json
{
  "action_id": "waf-application-gateway",
  "description": "Deploy Application Gateway v2 + WAF, closing T1595 gap",
  "cost": {
    "recurring_monthly_usd": null,
    "recurring_source": "Azure Pricing Calculator | Cost Management API | manual estimate",
    "implementation_hours_estimate": null,
    "implementation_hours_source": "manual estimate based on similar past work"
  },
  "secure_score_impact": {
    "category_guid": "f9d5432b-8f7b-45e9-b90c-e214a30f6a02",
    "category_name": "Restrict unauthorized network access",
    "points_available_in_category": 4,
    "points_current_in_category": 1.6,
    "verified_resources_affected": ["<resource IDs confirmed via az rest, not assumed>"],
    "verification_date": "2026-XX-XX",
    "verification_method": "az rest GET .../assessments, filtered by resource ID prefix matching this project's resource group"
  },
  "qualitative_value": {
    "attck_technique_closed": "T1595",
    "iso27001_control": "A.8.20 (docs/compliance/0020-a-8-20-networks-security.md)"
  }
}
```

## 5. Requirements (EARS notation)

### 5.1 Resource attribution and verification (directly addressing the Problem Statement's lesson)

- **REQ-01 (Ubiquitous):** Every claimed correlation between a remediation action and a Secure Score point gain shall be verified against actual resource IDs confirmed to belong to `django-azure-app`'s resource group(s) — never assumed from Secure Score category name matching alone.
- **REQ-02 (Unwanted behavior):** If a Secure Score control category's unhealthy resources include any belonging to a different project or resource group within the subscription, then the model shall attribute points only to the subset of resources confirmed to belong to `django-azure-app`, explicitly excluding the rest — a category being "unhealthy" at the subscription level does not mean this project is the cause.
- **REQ-03 (Event-driven):** When a new remediation action is proposed for this model, the analyst shall first query the specific resource IDs behind the relevant Secure Score category (per the `az rest .../providers/Microsoft.Security/assessments` pattern established 28.07.2026) before estimating any point gain.

### 5.2 Cost side of the model

- **REQ-04 (Ubiquitous):** Each remediation action's cost estimate shall record recurring Azure resource cost and one-time implementation effort (hours) as two separate fields — never blended into a single number.
- **REQ-05 (Ubiquitous):** Every cost figure shall cite its source explicitly (live Cost Management API query, Azure Pricing Calculator, or manual estimate) — no unsourced cost figures are permitted in the model's output.

### 5.3 Security-value side of the model

- **REQ-06 (Ubiquitous):** Each action's Secure Score impact shall be expressed using the verified current/max point values from the live `secureScoreControls` API for the specific, resource-attributed subset (per REQ-01/REQ-02) — never using assumed or category-wide weights.
- **REQ-07 (Optional feature):** Where a remediation action also closes a specific ATT&CK gap technique (cross-referenced against `attack_data.json`'s `evidence` array, once `evidence-linked-attack-mapping.spec.md` ships) or a specific ISO 27001 control (`docs/compliance/*.md`), the model shall record this as an additional qualitative value dimension, distinct from the numeric Secure Score points — since Secure Score alone does not capture full security value.

### 5.4 Output and ranking

- **REQ-08 (Ubiquitous):** The model shall produce two separate rankings — Secure Score percentage-points gained per dollar of monthly recurring cost, and percentage-points gained per hour of implementation effort — rather than a single blended score, since recurring cost and one-time effort are different resource types that shouldn't be conflated.
- **REQ-09 (Unwanted behavior):** If insufficient data exists to verify an action's resource attribution (REQ-01) or cost source (REQ-05), then that action shall be excluded from the ranked output and listed separately as "insufficient data" — never included in a ranking with an unverified estimate silently treated as fact.

## 6. Non-Functional Requirements

- **NFR-01:** This model is built entirely from read-only Azure API queries (`az rest GET` calls against Cost Management and Security assessment endpoints) — no Azure write access required, can be executed and refined now, independent of the current subscription billing block.
- **NFR-02:** This is a periodic, analyst-run exercise (re-run before each priority review), not a continuously-running feature — no new Azure resource, background job, or scheduled function is introduced by this spec.

## 7. Task Breakdown

**Why this section exists:** batching requirements avoids handing an AI coding agent a dozen-plus requirements in one shot, which risks context rot (see `docs/specs/TEMPLATE.md` section 7). Each batch below is sized for a single fresh Claude Code session.

| Batch | REQs covered | Description | Depends on | Azure write required? |
|---|---|---|---|---|
| 1 | REQ-01, REQ-02, REQ-03 | Build and apply the resource-attribution verification methodology — start by correctly resolving the "Remediate vulnerabilities" category (confirm 0 `django-azure-app` resources vs. the 8 `hornetdashboardprod` entries already found) | - | No (read-only) |
| 2 | REQ-04, REQ-05 | Collect cost-side data for the 4 known candidate actions (WAF/App Gateway, RBAC scope-down, `cryptography` update, PostgreSQL least-privilege) | Batch 1 | No (read-only Cost Management queries + Pricing Calculator lookups) |
| 3 | REQ-06, REQ-07 | Calculate verified Secure Score impact per action, using Batch 1's resource-level confirmation; cross-reference ATT&CK/ISO 27001 qualitative value | Batch 1 | No |
| 4 | REQ-08, REQ-09 | Produce the final ranked output (two separate rankings), explicitly excluding any action lacking verified data | Batch 1, 2, 3 | No |

## 8. Acceptance Criteria (checklist)

- [ ] Resource-level verification methodology documented and demonstrably applied to all 8 Secure Score categories (not assumed from category name for any of them)
- [ ] The "Remediate vulnerabilities" / `cryptography` correlation is explicitly corrected as this model's first real output, replacing the earlier unverified 36%→67% claim with a verified statement (confirmed impact, or confirmed non-impact, on this project specifically)
- [ ] At least 4 candidate remediation actions have both cost and Secure Score impact estimated using the full methodology (REQ-01 through REQ-07)
- [ ] Final output shows "cost per point" and "effort-hours per point" as two separate rankings, not one blended score
- [ ] Any action lacking verified resource attribution or cost sourcing is excluded from the ranking and explicitly flagged as "insufficient data"

## 9. Open Questions

1. Whether to build this as a manually-run markdown/spreadsheet report versus a small Python helper script that automates the `az rest` queries. **Recommendation:** start with a manual/lightly-scripted markdown report (`docs/research/security-cost-effectiveness-model.md` + a short Python helper for the repetitive `az rest` queries) — defer full dashboard automation until a Security Dashboard Phase 2 decision is made, consistent with this project's established principle of not over-engineering relative to its actual scale (4-8 candidate actions, not hundreds).
2. How to handle Secure Score categories where `points_available` is 0 (e.g., "Enable enhanced security features," confirmed 28.07.2026 to currently have 0 max points in this subscription) — remediating unhealthy resources there cannot show a point gain under the current scoring weights, making a cost-per-point ratio undefined. **Recommendation:** track these separately as "compliance/best-practice value, not Secure-Score-rankable" rather than forcing them into the cost-effectiveness ranking with a meaningless divide-by-zero ratio.

## 10. Traceability

This spec draws on real, already-existing project data sources: the FinOps Dashboard (`_all_cost_data()`), the Secure Score API (`secureScoreControls`, directly queried and verified 28.07.2026), `attack_data.json`'s planned `evidence` array (once `evidence-linked-attack-mapping.spec.md` ships — REQ-07 is optional and can be deferred until then), and the 34-file ISO 27001 compliance system in `docs/compliance/`. It is the first spec in this project to explicitly encode "verify resource attribution before claiming a cost/security correlation" as a hard requirement (REQ-01/REQ-02) — directly motivated by catching an incorrect assumption in the same session that proposed this spec. Independent of the other 7 specs in `docs/specs/README.md` for implementation, but methodologically continuous with the "verify-before-lock" discipline first established with the `ThreatIntelIndicators` correction (`ioc-reputation-lookup.spec.md`'s Revision Log) and repeated multiple times since.

## Revision Log

| Date | Change | Reason |
|---|---|---|
| 28.07.2026 | Initial draft created, built explicitly around correcting a same-day unverified claim (cryptography fix projected to raise Secure Score from 36% to ~67%, later found to likely be misattributed to a different project, `hornetdashboardprod`) | This R&D direction was proposed specifically because the FinOps+Secure-Score correlation attempt made earlier the same session turned out to be non-trivial — real evidence that a formal, verification-first methodology adds value beyond ad-hoc estimation |

---

## Requirement Traceability Verification (fill in only after implementation)

**Do not populate this section while authoring the spec.** This is a separate, post-implementation verification pass — ideally run in a fresh agent session, not the same conversation that wrote the implementation, to avoid the self-review blind spot. Prompt used for this pass:

> Audit the completed methodology/script against `docs/specs/security-investment-cost-effectiveness-model.spec.md`. For every requirement REQ-01 through REQ-09, provide: Status (satisfied / partially satisfied / missing), implementation file and symbol (or report section), test/verification evidence.

| REQ | Status | Implementation (file:symbol) | Test/Verification | Notes |
|---|---|---|---|---|
| REQ-01 | — | — | — | — |
| REQ-02 | — | — | — | — |

Only change this spec's **Status** field (top of file) from `Draft` to `Implemented` once this table is fully populated and every requirement is `satisfied` (or any `partially satisfied`/`missing` entries have been explicitly accepted as known limitations).