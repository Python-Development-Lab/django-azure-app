# Spec: Sentinel Rules Validation Trail

**Status:** Draft
**Feature ID:** SEC-DASH-VALIDATION-01
**Related backlog item:** Sentinel Rules Validation Trail (27.07.2026, from AdversaryGraph article comparison — "attack simulation for rule validation" concept, scoped down)
**Owner:** Vitalii Shevchuk
**Target surface:** `docs/security/rule-validation/` (new directory, markdown only)

---

## 1. Overview

Produce a documented validation trail for each of the 3 active Sentinel analytics rules, recording what telemetry each rule actually requires, what has genuinely fired in production, and what remains unverified. This is a documentation-only deliverable — no new Azure resources, no new code, no lab/simulation infrastructure.

## 2. Problem Statement

The 3 active Sentinel rules (`BuiltInFusion`, `zero-trust-device-verification`, `defender-active-scanning-nmap`) carry ATT&CK mappings and have fired on 2 real incidents to date, but there is no recorded evidence of what telemetry was actually required versus what fired, what conditions remain untested, or — critically — whether any of these 3 rules would have caught the newly discovered Critical Attack Path (App Service → Managed Identity → Key Vault, `c81dcadc-7b9c-3066-79cc-74be12d8b64f`). An unvalidated rule count is a materially weaker claim than a validated one, both for portfolio/certification purposes and for genuine security assurance.

## 3. Scope

**In scope:**
- One markdown record per rule (3 records) documenting the validation trail
- An explicit coverage check of the 3 existing rules against the newly discovered Critical Attack Path
- Cross-references to already-documented gaps (distributed password spray, automated response)

**Out of scope (explicitly deferred):**
- A full attack-simulation harness (staged/replayed attack traffic against the live environment) — no dedicated lab/sandbox environment exists, and building one is disproportionate to 3 rules and 2-3 known incidents
- Automated evidence population from live Sentinel APIs (manual documentation is sufficient at this scale, consistent with the Evidence-Linked ATT&CK Mapping spec's approach)
- Building the new detection rule for distributed password spray (that is tracked separately as its own backlog item; this spec only requires *noting* the gap in the relevant rule's trail, not closing it)

## 4. Data Model

**Directory structure:**
```
docs/security/rule-validation/
  README.md                                 (index, links to the 3 records + summary table)
  builtin-fusion.md
  zero-trust-device-verification.md
  defender-active-scanning-nmap.md
```

**Per-rule record structure (required sections, applies to all 3 files):**

1. **Rule identity** — name, severity, frequency (e.g., PT5M, PT1H, or ML for BuiltInFusion), ATT&CK technique(s) mapped
2. **Behavior claimed** — what attacker action the rule is meant to detect, in plain language
3. **Required telemetry** — exact table(s)/source(s) the rule logic depends on (e.g., `AppServiceHTTPLogs`, `AppTraces`, `SecurityAlert`), and confirmation that the relevant diagnostic setting routing that telemetry to `law-django-azure-staging` is active
4. **Expected event fields** — the specific KQL fields the rule's logic keys on (e.g., `CIp`, `ResultType`, `TimeGenerated` bucketing)
5. **What actually fired (evidence)** — link to real incident(s) with date, source IP if applicable, and outcome. Cross-reference the same incident IDs used in `attack_data.json`'s `evidence` array (per the Evidence-Linked ATT&CK Mapping spec) to avoid duplicate/drifting incident descriptions between the two documents.
6. **What remains unverified** — explicit, honest list of untested conditions or attack variants
7. **False-positive conditions** — any known benign triggers
8. **Automated response status** — whether a playbook/automated remediation is attached (expected: "none" for all 3 currently, per the still-open Automated Response Gap backlog item from 24.07.2026)

## 5. Requirements (EARS notation)

### 5.1 Content completeness

- **REQ-01 (Ubiquitous):** Each of the 3 rule validation records shall contain all 8 sections listed in section 4, with no section left as a placeholder or omitted.
- **REQ-02 (Ubiquitous):** Each record's "What actually fired" section shall cite only real, dated incidents already documented elsewhere in the project (this session's Attack Path finding, the NMap scan, the Zero Trust device alerts) — no hypothetical or illustrative incidents shall be presented as if they occurred.
- **REQ-03 (Unwanted behavior):** If a record's "What remains unverified" section is empty, then the record shall be treated as incomplete and rejected in review — every one of the 3 rules has at least one genuinely untested condition as of this spec's authoring date (e.g., the NMap rule has only fired on a single-source scan, not a distributed one), so an empty list signals the section was skipped, not that validation is total.

### 5.2 Critical Attack Path coverage check

- **REQ-04 (Ubiquitous):** The validation trail shall include an explicit determination, for each of the 3 rules, of whether that rule's required telemetry and logic would plausibly have detected the exploitation chain described in the Critical Attack Path `c81dcadc-7b9c-3066-79cc-74be12d8b64f` (App Service compromise → Managed Identity credential theft → Key Vault access).
- **REQ-05 (Event-driven):** When the coverage check in REQ-04 concludes that none of the 3 rules would have detected this chain, the validation trail's index (`README.md`) shall state this as an explicit, named detection gap — not bury it inside an individual rule's "unverified" list — since this is a cross-cutting finding relevant to the whole rule set, not one rule's limitation.

### 5.3 Cross-referencing existing gaps

- **REQ-06 (Optional feature):** Where the `defender-active-scanning-nmap` record's "What remains unverified" section discusses distributed/low-and-slow scanning or brute-force patterns, it shall reference the existing 24.07.2026 CyberDefenders AzureSpray backlog item (`FailCount>30 AND UniqueIPs>5` over 15m) rather than restating the gap independently.
- **REQ-07 (Ubiquitous):** Each record's "Automated response status" section shall reference the 24.07.2026 Automated Response Gap backlog item rather than treating the absence of a playbook as a newly discovered issue specific to that rule.

## 6. Non-Functional Requirements

- **NFR-01:** This is a pure documentation task — no code changes, no Terraform changes, no new Azure resources, and critically, no dependency on Azure write access (can be completed entirely while the subscription billing issue is unresolved).
- **NFR-02:** The 3 per-rule files plus the index shall use the C4-PlantUML documentation conventions already established in the project (ASCII-only, no em-dashes, for GitHub Actions rendering compatibility) where any diagrams are embedded — though diagrams are optional for this spec; the Evidence-Chain PlantUML Diagrams (separate backlog item) may later link to or embed within these same files rather than duplicating content.

## 7. Acceptance Criteria (checklist)

- [ ] `docs/security/rule-validation/README.md` exists with a summary table (rule name, severity, evidence count, unverified-conditions count, automated-response status) and links to all 3 per-rule files
- [ ] `builtin-fusion.md`, `zero-trust-device-verification.md`, `defender-active-scanning-nmap.md` each contain all 8 required sections
- [ ] The Critical Attack Path coverage check (REQ-04/REQ-05) is completed and its conclusion is stated explicitly in the index, not only inside individual rule files
- [ ] The distributed password spray gap and automated response gap are referenced (not restated) per REQ-06/REQ-07
- [ ] Incident dates/IDs match exactly between this validation trail and the `evidence` array in `attack_data.json` (per the Evidence-Linked ATT&CK Mapping spec) — no drift between the two documents' descriptions of the same incidents

## 8. Open Questions

1. Whether `BuiltInFusion` (an ML-based, Microsoft-managed correlation rule rather than a custom KQL rule) can meaningfully have a "required telemetry" section in the same sense as the other two custom rules — Microsoft does not expose the exact internal logic of Fusion rules. Recommendation: document this limitation explicitly in `builtin-fusion.md` itself (i.e., the record's own "required telemetry" section should state that Fusion's internal correlation logic is not user-inspectable, and describe only the *inputs* — which data sources feed into Sentinel that Fusion could draw from — rather than claiming a false level of transparency into a Microsoft-managed rule.
2. Whether the Critical Attack Path coverage check (REQ-04) should be performed by manually reading each rule's KQL query and reasoning about it, or whether there is a faster way to check historically (e.g., searching `SecurityAlert`/`SecurityIncident` for any alert correlated with the specific resources involved in the attack path around the time it was likely exploitable). Recommendation: start with manual KQL/logic review (no Azure write access needed, can be done now); the historical correlation search can be a follow-up once Azure write/query access is confirmed stable again.

## 9. Traceability

This spec operationalizes the "Sentinel Rules Validation Trail" backlog item (27.07.2026). It shares incident-evidence data with the Evidence-Linked ATT&CK Mapping spec (`docs/specs/evidence-linked-attack-mapping.spec.md`) — both must stay in sync on incident dates/IDs (see REQ-02 and the final acceptance criterion). It is independent of the IOC Reputation Lookup spec (`docs/specs/ioc-reputation-lookup.spec.md`), which touches a different code path with no overlap. This spec is also the natural precursor to the separately-tracked Evidence-Chain PlantUML Diagrams backlog item — once this validation trail exists in prose form, the PlantUML diagrams can visualize the same 8-section chain rather than being authored independently.
## Revision Log

| Date | Change | Reason |
|---|---|---|
| 28.07.2026 | Initial draft created, including REQ-04/REQ-05 (Critical Attack Path coverage check) from the outset | Authored after the Critical Attack Path (`c81dcadc-7b9c-3066-79cc-74be12d8b64f`) was already confirmed in the same session, so the coverage-check requirement was built in from the first draft rather than added as a later revision |
