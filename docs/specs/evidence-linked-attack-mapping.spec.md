# Spec: Evidence-Linked ATT&CK Mapping

**Status:** Draft
**Feature ID:** SEC-DASH-EVIDENCE-01
**Related backlog item:** Evidence-Linked ATT&CK Mapping + IOC Reputation Lookup (27.07.2026)
**Owner:** Vitalii Shevchuk
**Target surface:** `security/mitre/attack_data.json`, `templates/core/partials/security_coverage.html`

---

## 1. Overview

Extend the existing static ATT&CK coverage matrix (`attack_data.json`) so that each technique can carry zero or more **evidence entries** linking a coverage claim to a real, observed security event. The coverage graph and matrix must visually distinguish "claimed" coverage from "evidence-backed" coverage without introducing a new database, a new API endpoint, or a new backend service.

## 2. Problem Statement

The current schema classifies each of the 20 techniques as `mitigated` / `detected` / `monitored` / `gap` as a flat label with no connection to real incidents. This is a theoretical claim, not a verified one. Two real incidents already exist (NMap scan 2026-06-26; Zero Trust device alerts) and one Critical Defender for Cloud Attack Path (App Service → Managed Identity → Key Vault, driven by an outdated `cryptography` package) — none of these are currently reflected in the technique data.

## 3. Scope

**In scope:**
- JSON schema extension to `attack_data.json`
- Manual population of evidence for currently-known incidents
- Visual differentiation in the existing D3.js graph and coverage matrix table
- Build-time validation of evidence entries

**Out of scope (explicitly deferred):**
- Automatic evidence population from live Sentinel/Defender APIs (background job/webhook)
- A dedicated graph database or new data store (defer to Security Dashboard Phase 2 decision)
- Claims/detection-candidates as separate first-class entities (full Evidence-to-Detection Graph) — not justified at current scale (20 techniques, 3 known incidents)

## 4. Data Model

`security/mitre/attack_data.json` — **confirmed via direct file read, 28.07.2026** (see Revision Log). Actual structure is a **nested** tactic→technique tree, not a flat list:

```json
{
  "project": "django-azure-security-template",
  "tactics": [
    {
      "id": "TA0001",
      "name": "Initial Access",
      "techniques": [
        {
          "id": "T1078",
          "name": "Valid Accounts",
          "status": "mitigated",
          "control": "Entra ID OAuth2 + MFA (Security Defaults)",
          "detection": "Sentinel Sign-in risk analytics"
        }
      ]
    }
  ]
}
```

**Corrected from the originally-drafted version of this spec, which incorrectly assumed a flat array with a `technique_id` field and a sibling `tactic` field.** The real field for technique ID is simply `id`, nested under the parent tactic's `techniques` array — the tactic is implied by nesting, not stated on the technique itself. See Revision Log for the correction history.

**Design decision for the `evidence` array given the real (nested) schema:** the `evidence` array is added as a new sibling field on each technique object, alongside `id`, `name`, `status`, `control`, `detection` — not as a separate flat structure. Example:

```json
{
  "id": "T1595",
  "name": "Active Scanning",
  "status": "gap",
  "control": "No WAF or IP restriction rules configured",
  "detection": "Defender for App Service detected NMap (T1595.001)",
  "evidence": [
    {
      "incident_date": "2026-06-26",
      "source": "defender-active-scanning-nmap",
      "source_ip": "20.61.126.211",
      "target": "/auth/login/",
      "detected_by": "defender-active-scanning-nmap",
      "sentinel_incident_ref": null,
      "attack_path_id": null
    }
  ]
}
```

Field `attack_path_id` is used when evidence originates from a Defender for Cloud Attack Path (e.g., `c81dcadc-7b9c-3066-79cc-74be12d8b64f` for the App Service → Key Vault path) rather than a Sentinel alert.

### 4.1 Confirmed evidence entries for the Critical Attack Path

**Important correction (28.07.2026):** the example below was originally written assuming a flat structure with a `technique_id` field. The real file uses `id`, nested under each tactic's `techniques` array (per section 4). Additionally, direct comparison against the live file surfaced two real conflicts, now tracked as Open Question 3 below — **do not populate these entries as-is without resolving that question first.**

The App Service → Managed Identity → Key Vault path (`c81dcadc-7b9c-3066-79cc-74be12d8b64f`, Critical severity, root cause: outdated `cryptography` package) touches four techniques across two tactics:

| Technique | `id` | Current status in live file | Action needed |
|---|---|---|---|
| Unsecured Credentials | `T1552` | **Already exists**, status `mitigated` (control: "Azure Key Vault + System-Assigned Managed Identity") | **Conflict** — see Open Question 3 |
| Password Managers | `T1555.005` | **Does not exist** in `TA0006` (Credential Access) | New technique entry needed |
| Remote Services | `T1021` | **Does not exist** — no `TA0008` (Lateral Movement) tactic exists in the file at all | New tactic (`TA0008`) + new technique entry needed |
| Cloud Services | `T1021.007` | **Does not exist** — same `TA0008` gap as above | New technique entry needed, under the same new `TA0008` tactic |

Example of a *new* technique entry (for `T1021`, illustrating the corrected nested schema and requiring a new `TA0008` tactic wrapper — not yet resolved, see Open Question 3):

```json
{
  "id": "TA0008",
  "name": "Lateral Movement",
  "techniques": [
    {
      "id": "T1021",
      "name": "Remote Services",
      "status": "gap",
      "control": "No detection or restriction on Managed Identity token use across services",
      "detection": "No coverage yet",
      "evidence": [
        {
          "incident_date": "2026-07-27",
          "source": "defender-cspm-attack-path-analysis",
          "detected_by": "Attack Path Analysis: Internet exposed Azure Web App with high severity vulnerabilities allows lateral movement to Critical Azure Key Vault",
          "attack_path_id": "c81dcadc-7b9c-3066-79cc-74be12d8b64f",
          "note": "Attacker authenticates as the Managed Identity to reach Key Vault."
        }
      ]
    }
  ]
}
```

Example of adding evidence to the *existing* `T1552` entry (illustrative only — status value shown as `TBD` pending Open Question 3's resolution):

```json
{
  "id": "T1552",
  "name": "Unsecured Credentials",
  "status": "TBD — see Open Question 3",
  "control": "Azure Key Vault + System-Assigned Managed Identity",
  "detection": "Key Vault audit logs",
  "evidence": [
    {
      "incident_date": "2026-07-27",
      "source": "defender-cspm-attack-path-analysis",
      "detected_by": "Attack Path Analysis: Internet exposed Azure Web App with high severity vulnerabilities allows lateral movement to Critical Azure Key Vault",
      "attack_path_id": "c81dcadc-7b9c-3066-79cc-74be12d8b64f",
      "note": "Root cause: outdated cryptography package on app-django-azure-staging currently allows the general Key Vault mitigation to be bypassed via App Service compromise."
    }
  ]
}
```

All new/modified entries reference the same `attack_path_id` (`c81dcadc-7b9c-3066-79cc-74be12d8b64f`). Once the `cryptography` package is patched and the path is closed, evidence entries are retained (per REQ-12's `remediated_date` field), not deleted.

## 5. Requirements (EARS notation)

### 5.1 Data layer

- **REQ-01 (Ubiquitous):** The system shall support zero or more evidence entries per technique in `attack_data.json`.
- **REQ-02 (Ubiquitous):** The system shall treat a technique with an empty `evidence` array as "theoretically mapped, not yet verified."
- **REQ-03 (Unwanted behavior):** If an evidence entry references a technique `id` that does not exist anywhere in the `tactics[].techniques[]` tree, then the build/validation step shall fail with a clear error identifying the invalid entry.
- **REQ-04 (Unwanted behavior):** If an evidence entry is missing `incident_date` or `detected_by`, then validation shall fail — every evidence entry must be independently traceable.
- **REQ-12 (Event-driven):** When a gap identified by an evidence entry is remediated, the system shall retain the original evidence entry and add a `remediated_date` field rather than deleting the entry — evidence is a historical record, not a live-status field.

### 5.2 Visualization layer (D3.js graph)

- **REQ-05 (State-driven):** While a technique has one or more evidence entries, the D3.js graph shall render that node with a distinct visual marker (e.g., a checkmark badge or border highlight) not used for evidence-less nodes.
- **REQ-06 (State-driven):** While a technique has zero evidence entries, the graph shall render it using the current (existing) 4-color status scheme with no additional marker.
- **REQ-07 (Event-driven):** When a user hovers over or selects an evidence-marked node, the system shall display a tooltip or side panel listing each evidence entry's `incident_date`, `source_ip` (if present), and `detected_by`.

### 5.3 Coverage matrix table

- **REQ-08 (Ubiquitous):** The coverage matrix table shall include an "Evidence count" column showing the number of evidence entries per technique (0, 1, 2...).
- **REQ-09 (Optional feature):** Where the "Evidence count" column is present, the table shall support sorting by that column.

### 5.4 Linking to incident sources

- **REQ-10 (Optional feature):** Where an evidence entry has a non-null `sentinel_incident_ref`, the tooltip/panel shall render it as a link-style reference (text is sufficient; a live hyperlink to Sentinel is not required in this iteration).
- **REQ-11 (Optional feature):** Where an evidence entry has a non-null `attack_path_id`, the tooltip/panel shall display it as plain text (matching the ID format used in Defender for Cloud Attack Path URLs) for manual cross-reference by the operator.

## 6. Non-Functional Requirements

- **NFR-01:** No new HTMX endpoint, Django view, or database migration is required — this is a static JSON schema extension consumed by the existing coverage-loading code path.
- **NFR-02:** No new Azure resources, API calls, or Terraform changes.
- **NFR-03:** Validation (REQ-03, REQ-04) shall run as part of the existing CI pipeline (a simple JSON schema check step is sufficient — no new pipeline job required if it can be folded into an existing lint/test step).

## 7. Task Breakdown

**Why this section exists:** batching requirements avoids handing an AI coding agent a dozen-plus requirements in one shot, which risks context rot (see `docs/specs/TEMPLATE.md` section 7 for the full rationale). Each batch below is sized for a single fresh Claude Code session. **Note (28.07.2026):** Batch 1 now also includes creating the new `TA0008` tactic entry and resolving the `T1552` status conflict per Open Question 3 — this makes Batch 1 slightly larger in practice than originally scoped, but still a single coherent unit of work (all schema-level changes).

| Batch | REQs covered | Description | Depends on | Azure write required? |
|---|---|---|---|---|
| 1 | REQ-01, REQ-02, REQ-03, REQ-04, REQ-12 | Data schema (`evidence` array) + validation (unknown technique `id`, missing required fields) + remediation tracking (`remediated_date`) + create `TA0008` tactic + resolve `T1552` status conflict (Open Question 3) | - | No |
| 2 | REQ-05, REQ-06, REQ-07 | D3.js graph visual marker for evidence-backed nodes + hover tooltip/panel | Batch 1 | No |
| 3 | REQ-08, REQ-09 | Coverage matrix table: sortable "Evidence count" column | Batch 1 | No |
| 4 | REQ-10, REQ-11 | Link evidence entries to Sentinel incident refs / Attack Path IDs in the tooltip | Batch 1 | No |

## 8. Acceptance Criteria (checklist)

- [ ] `attack_data.json` schema documented with the `evidence` field (optional, array, can be empty)
- [ ] Evidence populated for: NMap scan (T1595, T1046), Zero Trust device alerts (T1078, T1036) — straightforward, no conflicts. Critical Attack Path finding: T1552 (Unsecured Credentials, **status conflict to resolve — Open Question 3**), T1555.005 (Password Managers, **new entry**), T1021 (Remote Services, **new entry, new `TA0008` tactic**), T1021.007 (Cloud Services, **new entry**) — see section 4.1
- [ ] D3.js graph visually distinguishes evidence-backed nodes from theoretical-only nodes
- [ ] Coverage matrix table has a sortable "Evidence count" column
- [ ] CI fails the build if an evidence entry is malformed or references an unknown technique
- [ ] No regressions to existing `/security/coverage/` load time or the existing 4-color status scheme

## 9. Open Questions

1. ~~Exact technique ID and tactic for the second MITRE ATT&CK icon shown in the Defender for Cloud Attack Path screen~~ **RESOLVED (28.07.2026):** confirmed via direct portal inspection. The Critical Attack Path (`c81dcadc-7b9c-3066-79cc-74be12d8b64f`) maps to four techniques across two tactics:

   | Tactic | Technique ID | Name |
   |---|---|---|
   | Lateral Movement | T1021 | Remote Services |
   | Lateral Movement | T1021.007 | Cloud Services |
   | Credential Access | T1552 | Unsecured Credentials |
   | Credential Access | T1555.005 | Password Managers |

   Note: T1555.005 ("Password Managers") is Microsoft's classification of the Key Vault credential-theft step within this attack path — not a literal password-manager application. This should be noted inline in the evidence entry's `detected_by`/context field to avoid confusion during future review.

2. Whether `attack_path_id` should eventually support a live deep-link to the Azure Portal Attack Path view (would require storing the full portal URL pattern, which is version-dependent — see prior discussion on portal deep-link fragility). Decision: keep as plain-text ID for now; revisit only if the deep-link pattern proves stable across portal sessions.

3. **NEW, CRITICAL (28.07.2026):** Direct comparison of section 4.1 against the real, live `attack_data.json` file surfaced two real conflicts that must be resolved before implementation:
   - **T1552 status conflict:** the live file already classifies `T1552` (Unsecured Credentials) as `mitigated` (control: "Azure Key Vault + System-Assigned Managed Identity"). The Critical Attack Path evidence shows this mitigation is currently *bypassable* via the outdated `cryptography` vulnerability. **Needs a decision, not a silent fix:** (a) keep status `mitigated` and let the evidence array alone convey "the general control exists but has a currently-open bypass," or (b) change status to `gap` while the bypass remains unpatched, reverting to `mitigated` once `cryptography` is updated (per REQ-12's `remediated_date` pattern). **Recommendation:** option (b) — a technique whose control is actively bypassable in production is more honestly represented as `gap` than `mitigated`; this is consistent with the project's broader "Honest Limitations" principle (see `security-md-honest-limitations.spec.md`) of not overstating current protection.
   - **Missing tactic and technique entries:** `T1021`, `T1021.007` (Lateral Movement) and `T1555.005` (Password Managers, under Credential Access) do not exist anywhere in the current file. Unlike the original assumption ("add evidence to existing entries"), implementing this spec now also requires **creating a brand-new `TA0008` (Lateral Movement) tactic entry** — a larger, more structural change than originally scoped. This should be called out explicitly to whoever implements this spec (do not let it be discovered mid-implementation as a surprise).

## Additional Findings (discovered during verification, outside this spec's own scope)

Two additional findings surfaced while reading the live file, unrelated to this spec's own requirements but worth recording so they aren't lost:

- **Project-wide status counts are stale.** Every prior reference in this project (backlog notes, the Security Dashboard baseline spec) states coverage as "6 mitigated / 8 detected / 1 monitored / 5 gap." The actual live file shows **6 mitigated / 5 detected / 1 monitored / 8 gap** — a materially different split, with 3 more gap techniques than previously documented (`T1068`, `T1110.004`, `T1528` — all tied to the already-known KBSSE/RiskScoringMiddleware-not-implemented finding from 25.07.2026). `security-dashboard-baseline.spec.md`'s REQ-08 has been corrected accordingly (see that file's own Revision Log).
- **Possible additional misclassification:** `T1567` (Exfiltration Over Web Service) is marked `detected`, with its `detection` field crediting "RiskScoringMiddleware volume/pattern analysis" — but `RiskScoringMiddleware` is confirmed (25.07.2026 session) to not exist as real code. This technique may be misclassified as `detected` when it should be `gap`, consistent with the other three KBSSE-dependent techniques. Not fixed here — flagged for a separate, dedicated review of the file's `detected` classifications against actually-implemented code, since that review is broader than this spec's scope.

## 10. Traceability

This spec directly implements the "Evidence-Linked ATT&CK Mapping" half of the 27.07.2026 backlog item. The IOC Reputation Lookup half of that backlog item is a separate, independent spec (not covered here) since it touches a different code path (`_get_defender_alerts()`) with no data-model overlap.

## Revision Log

| Date | Change | Reason |
|---|---|---|
| 27.07.2026 | Initial draft created | Formalizes the "Evidence-Linked ATT&CK Mapping" half of the AdversaryGraph-comparison backlog item |
| 28.07.2026 (a) | Open Question 1 resolved; section 4.1 added with 4 confirmed evidence entries (T1552, T1555.005, T1021, T1021.007); REQ-12 added (remediation tracking, `remediated_date`); acceptance criteria checklist updated | Direct portal inspection of the Critical Attack Path's MITRE ATT&CK tactics panel confirmed the exact technique IDs, replacing the placeholder "likely T1021, to be confirmed" |
| 28.07.2026 (b) | Major correction: Data Model (section 4) rewritten from a flat `technique_id`-based schema to the real nested `tactics[].techniques[].id` schema, confirmed via direct read of the live `attack_data.json` file (Security Dashboard baseline spec's Verification Batch 4). Section 4.1's JSON examples rebuilt to match. REQ-03 field-name reference corrected. New Open Question 3 added (T1552 status conflict + missing `TA0008`/`T1021`/`T1021.007`/`T1555.005` entries). Added missing Task Breakdown section (7) to match the version already present in the actual repository — this local copy had fallen out of sync with the retroactive Task Breakdown insertion applied earlier. Added "Additional Findings" section documenting the project-wide stale status-count discovery (6/8/1/5 claimed vs. 6/5/1/8 actual) and a possible `T1567` misclassification, both out of this spec's scope but logged for follow-up. Acceptance criteria updated to reflect conflicts rather than false confirmation. | This is the most significant "verify-before-lock" catch of the session — the spec's central data-model assumption (flat schema, `technique_id` field) was wrong, and two of its four "confirmed" evidence entries actually require new tactic/technique creation or a real status conflict resolution rather than a simple evidence-array addition |