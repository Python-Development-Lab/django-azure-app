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

Each technique entry in `attack_data.json` gains an optional `evidence` array:

```json
{
  "technique_id": "T1595",
  "status": "detected",
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

The App Service → Managed Identity → Key Vault path (`c81dcadc-7b9c-3066-79cc-74be12d8b64f`, Critical severity, root cause: outdated `cryptography` package) produces **four** evidence entries across two tactics, all sharing the same `attack_path_id`:

```json
[
  {
    "technique_id": "T1552",
    "status": "gap",
    "evidence": [
      {
        "incident_date": "2026-07-27",
        "source": "defender-cspm-attack-path-analysis",
        "detected_by": "Attack Path Analysis: Internet exposed Azure Web App with high severity vulnerabilities allows lateral movement to Critical Azure Key Vault",
        "attack_path_id": "c81dcadc-7b9c-3066-79cc-74be12d8b64f",
        "note": "Tactic: Credential Access. Root cause: outdated cryptography package on app-django-azure-staging enabling lateral movement to kv-django-azure-staging."
      }
    ]
  },
  {
    "technique_id": "T1555.005",
    "status": "gap",
    "evidence": [
      {
        "incident_date": "2026-07-27",
        "source": "defender-cspm-attack-path-analysis",
        "detected_by": "Attack Path Analysis: Internet exposed Azure Web App with high severity vulnerabilities allows lateral movement to Critical Azure Key Vault",
        "attack_path_id": "c81dcadc-7b9c-3066-79cc-74be12d8b64f",
        "note": "Tactic: Credential Access. Microsoft's classification of Key Vault credential-theft step within this attack path -- not a literal password-manager application."
      }
    ]
  },
  {
    "technique_id": "T1021",
    "status": "gap",
    "evidence": [
      {
        "incident_date": "2026-07-27",
        "source": "defender-cspm-attack-path-analysis",
        "detected_by": "Attack Path Analysis: Internet exposed Azure Web App with high severity vulnerabilities allows lateral movement to Critical Azure Key Vault",
        "attack_path_id": "c81dcadc-7b9c-3066-79cc-74be12d8b64f",
        "note": "Tactic: Lateral Movement. Attacker authenticates as the Managed Identity to reach Key Vault."
      }
    ]
  },
  {
    "technique_id": "T1021.007",
    "status": "gap",
    "evidence": [
      {
        "incident_date": "2026-07-27",
        "source": "defender-cspm-attack-path-analysis",
        "detected_by": "Attack Path Analysis: Internet exposed Azure Web App with high severity vulnerabilities allows lateral movement to Critical Azure Key Vault",
        "attack_path_id": "c81dcadc-7b9c-3066-79cc-74be12d8b64f",
        "note": "Tactic: Lateral Movement (Cloud Services sub-technique). Cloud-native equivalent of T1021 specific to Managed Identity authentication."
      }
    ]
  }
]
```

All four entries are marked `status: "gap"` (not `mitigated`/`detected`) since the remediation (updating `cryptography`, tightening Managed Identity permissions, hardening internet exposure per Defender's "Additional recommendations") has not yet been applied as of this spec's authoring date. Once remediated, these statuses should be revisited and the evidence entries kept as historical record (do not delete evidence when a gap is closed -- append a `remediated_date` field instead, see REQ-12 below).

## 5. Requirements (EARS notation)

### 5.1 Data layer

- **REQ-01 (Ubiquitous):** The system shall support zero or more evidence entries per technique in `attack_data.json`.
- **REQ-02 (Ubiquitous):** The system shall treat a technique with an empty `evidence` array as "theoretically mapped, not yet verified."
- **REQ-03 (Unwanted behavior):** If an evidence entry references a `technique_id` that does not exist in the technique list, then the build/validation step shall fail with a clear error identifying the invalid entry.
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

**Why this section exists:** batching requirements avoids handing an AI coding agent a dozen-plus requirements in one shot, which risks context rot (see `docs/specs/TEMPLATE.md` section 7 for the full rationale). Each batch below is sized for a single fresh Claude Code session.

| Batch | REQs covered | Description | Depends on | Azure write required? |
|---|---|---|---|---|
| 1 | REQ-01, REQ-02, REQ-03, REQ-04, REQ-12 | Data schema (`evidence` array) + validation (unknown `technique_id`, missing required fields) + remediation tracking (`remediated_date`) | - | No |
| 2 | REQ-05, REQ-06, REQ-07 | D3.js graph visual marker for evidence-backed nodes + hover tooltip/panel | Batch 1 | No |
| 3 | REQ-08, REQ-09 | Coverage matrix table: sortable "Evidence count" column | Batch 1 | No |
| 4 | REQ-10, REQ-11 | Link evidence entries to Sentinel incident refs / Attack Path IDs in the tooltip | Batch 1 | No |

## 8. Acceptance Criteria (checklist)

- [ ] `attack_data.json` schema documented with the `evidence` field (optional, array, can be empty)
- [ ] Evidence populated for: NMap scan (T1595, T1046), Zero Trust device alerts (T1078, T1036), and the Critical Attack Path finding — **confirmed** four entries: T1552 (Unsecured Credentials), T1555.005 (Password Managers), T1021 (Remote Services), T1021.007 (Cloud Services) — see section 4.1
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

## 10. Traceability

This spec directly implements the "Evidence-Linked ATT&CK Mapping" half of the 27.07.2026 backlog item. The IOC Reputation Lookup half of that backlog item is a separate, independent spec (not covered here) since it touches a different code path (`_get_defender_alerts()`) with no data-model overlap.

## Revision Log

| Date | Change | Reason |
|---|---|---|
| 27.07.2026 | Initial draft created | Formalizes the "Evidence-Linked ATT&CK Mapping" half of the AdversaryGraph-comparison backlog item |
| 28.07.2026 | Open Question 1 resolved; section 4.1 added with 4 confirmed evidence entries (T1552, T1555.005, T1021, T1021.007); REQ-12 added (remediation tracking, `remediated_date`); acceptance criteria checklist updated | Direct portal inspection of the Critical Attack Path's MITRE ATT&CK tactics panel confirmed the exact technique IDs, replacing the placeholder "likely T1021, to be confirmed" |
