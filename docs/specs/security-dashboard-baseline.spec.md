# Spec: Security Dashboard — Baseline (Retroactive)

**Status:** Implemented
**Feature ID:** `SEC-DASH-BASELINE-01`
**Related backlog item:** N/A — this is retroactive documentation of pre-SDD work (built June-July 2026, before Spec-Driven Development was adopted for this project on 28.07.2026)
**Owner:** Vitalii Shevchuk
**Target surface:** `core/views.py`, `templates/core/security.html` + `templates/core/partials/security_coverage.html` / `security_alerts.html`, `security/mitre/attack_data.json`

---

## 1. Overview

This spec retroactively documents the **already-built, already-working** Security Dashboard (`/security/`) as a formal, verifiable EARS contract — the first application of Tier 2 (Spec-Anchored) discipline in this project, per the SDD maturity model discussed in this session's article reviews. This is **not** a design document for new work: it captures current, real behavior so that (a) future changes to this subsystem can be checked against a known-good baseline rather than against tribal knowledge, and (b) the 3 forward-looking specs that extend this subsystem (`evidence-linked-attack-mapping.spec.md`, `sentinel-rules-validation-trail.spec.md`, `evidence-chain-plantuml-diagrams.spec.md`) have a documented foundation to build on rather than an implicit, undocumented one.

## 2. Problem Statement

Before this session, `django-azure-app` had no formal spec for any subsystem — only prose descriptions scattered across project memory and backlog notes. For the Security Dashboard specifically, this meant there was no single, testable contract describing what `/security/` actually does, which made it harder to confidently hand future dashboard changes to an AI coding agent with a clear "this must still be true" baseline. This is a pilot: if it proves useful, other subsystems (FinOps Dashboard, CI/CD pipeline, Terraform modules) may get the same retroactive treatment later; if not, this documents the lesson learned either way.

## 3. Scope

**In scope:**
- Documenting the existing HTMX shell-loading pattern for `/security/`
- Documenting the existing `/security/coverage/` endpoint (D3.js ATT&CK graph + coverage matrix, sourced from `attack_data.json`)
- Documenting the existing `/security/alerts/` endpoint (live Defender for Cloud alerts via MSI Security Reader role)
- Documenting the currently-known real data points (technique classification counts, confirmed real incidents) as of this baseline's authoring date

**Out of scope (explicitly deferred):**
- FinOps Dashboard, CI/CD pipeline, Terraform modules, or any other subsystem — this is a single-subsystem pilot, not a project-wide baselining effort
- The NOT-yet-implemented additions from the 3 forward-looking specs (evidence array, validation trail docs, PlantUML diagrams) — those remain separate Draft specs describing future work; this baseline captures only what is live *today*, before those specs are implemented
- Re-deriving full source code as prose — this spec describes the behavioral contract at a level a reader can verify against the running system, not a line-by-line code walkthrough

## 4. Data Model

`security/mitre/attack_data.json` — **confirmed via direct file read, 28.07.2026** (Verification Batch 4 completed). Real structure is a **nested** tactic→technique tree:

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

**This corrects the originally-drafted version of this section**, which had inferred a flat schema with a `technique_id` field and a sibling `tactic` field — that inference was wrong. The real field for technique ID is `id`, nested under each tactic's `techniques` array. Open Question 1 (below) is now resolved with this finding rather than left as an inference. See Revision Log.

## 5. Requirements (EARS notation) — describing existing, live behavior

### 5.1 Dashboard shell loading

- **REQ-01 (Ubiquitous):** `GET /security/` shall return an HTML shell that renders in the browser without waiting for backend Defender/Sentinel API calls to complete.
- **REQ-02 (Event-driven):** When the shell has loaded, the browser shall trigger parallel HTMX requests to `/security/coverage/` and `/security/alerts/` (`hx-trigger="load"`).

### 5.2 ATT&CK coverage graph and matrix

- **REQ-03 (Ubiquitous):** `GET /security/coverage/` shall render a D3.js force-directed graph of the technique set defined in `attack_data.json`.
- **REQ-04 (Ubiquitous):** Each node in the graph shall be colored according to one of 4 status categories: `mitigated`, `detected`, `monitored`, `gap`.
- **REQ-05 (Ubiquitous):** The endpoint shall also render a tabular coverage matrix listing all techniques with their status and tactic grouping.

### 5.3 Defender alerts panel

- **REQ-06 (Ubiquitous):** `GET /security/alerts/` shall query Microsoft Defender for Cloud's `SecurityAlert` data using the App Service's System-Assigned Managed Identity (Security Reader role) — no `client_id` is used, per the project's established MSI pattern.
- **REQ-07 (Ubiquitous):** The endpoint shall render each retrieved alert with at minimum its title/description, severity, and detection timestamp.

### 5.4 Known verified data points as of this baseline (28.07.2026)

- **REQ-08 (Ubiquitous):** As of this baseline's authoring date, the technique set shall classify **6** techniques as `mitigated`, **5** as `detected`, **1** as `monitored`, and **8** as `gap`, totaling 20 techniques across 9 tactics. **(Corrected 28.07.2026 — see Revision Log; the figure "8 detected / 5 gap" used throughout this project prior to this verification was stale/incorrect. The real gap list includes 3 techniques not previously named in any project document — `T1068`, `T1110.004`, `T1528` — all tied to the KBSSE/`RiskScoringMiddleware`-not-implemented finding from 25.07.2026.)**
- **REQ-09 (Ubiquitous):** The alerts data source shall include at minimum one real, independently-confirmed incident: an NMap scan (2026-06-26, source IP `20.61.126.211`, target `/auth/login/`), plus a set of 15 recorded Zero Trust device verification alerts.

## 6. Non-Functional Requirements

- **NFR-01:** This subsystem requires an active, `Enabled` Azure subscription with working MSI role assignments (Security Reader) for `/security/alerts/` to function. During the current billing-block period (see 27–28.07.2026 session notes), live testing of this endpoint against real Defender data is not possible, though the static `/security/coverage/` graph (backed by the local `attack_data.json` file) is unaffected by the Azure billing issue.
- **NFR-02:** This baseline spec introduces no new infrastructure — it documents existing resources (`law-django-azure-staging`, existing MSI role assignments) rather than creating new ones.

## 7. Task Breakdown (Verification Batches)

**Why "verification" rather than "implementation":** the code behind every requirement above already exists and is live. The batches below are re-framed as verification checks — confirming the spec accurately describes real behavior — rather than build tasks.

| Batch | REQs covered | Verification action | Depends on | Azure access required? |
|---|---|---|---|---|
| 1 | REQ-01, REQ-02 | Manually load `/security/` in a browser; confirm shell renders instantly and both HTMX panels fire in parallel | - | No (App Service must be reachable, but this is a read-only check) |
| 2 | REQ-03, REQ-04, REQ-05 | Open `/security/coverage/`; confirm graph renders with 4-color scheme and matrix table lists all techniques | - | No — sourced from local JSON file |
| 3 | REQ-06, REQ-07 | Open `/security/alerts/`; confirm real Defender alerts render with title, severity, timestamp | - | Yes — requires stable Azure access (currently blocked by billing issue) |
| 4 | REQ-08, REQ-09 | Re-open `attack_data.json` directly and re-count status categories; re-confirm the NMap and Zero Trust incidents are still present in the alerts data | - | No for the file check; Yes for re-confirming live alert data |

## 8. Acceptance Criteria (checklist)

- [x] REQ-01/REQ-02 — asserted true based on project documentation describing this exact pattern (HTMX shell + parallel `hx-trigger="load"`); **not freshly re-observed in-browser this session** — treat as "documented, not re-verified" (Verification Batch 1 still pending)
- [x] **REQ-08 counts corrected and verified (28.07.2026)** — direct read of `attack_data.json` confirms **6 mitigated / 5 detected / 1 monitored / 8 gap** (not 6/8/1/5 as originally stated); 20 techniques, 9 tactics both confirmed correct
- [x] REQ-09 (NMap incident, Zero Trust alerts) — independently corroborated multiple times this session (Attack Path analysis, Sentinel rule descriptions), and the NMap incident is directly confirmed in the live file's own `detection` field for `T1046` — **highest confidence item in this checklist**
- [ ] REQ-03/04/05 — schema confirmed (see section 4), but the actual rendered `/security/coverage/` HTML/D3.js output has still not been visually inspected this session — Verification Batch 2 partially complete (data source confirmed, rendering not yet confirmed)
- [ ] REQ-06/07 — cannot be verified live until Azure subscription billing is resolved and `/security/alerts/` is reachable with working MSI access

## 9. Open Questions

1. ~~The exact current JSON schema of `attack_data.json`~~ **RESOLVED (28.07.2026):** confirmed via direct file read (Verification Batch 4). Real schema is the nested `tactics[].techniques[]` tree described in section 4 — not the flat `technique_id`-based structure originally inferred. This also required a correction to `evidence-linked-attack-mapping.spec.md`, which had made the same wrong inference (see that file's own Revision Log). Additionally discovered: `T1567` is classified `detected` with detection method "RiskScoringMiddleware volume/pattern analysis" — but that middleware is confirmed (25.07.2026 session) to not exist as real code, suggesting a possible misclassification not yet corrected in the live file. This is logged here for awareness but is out of this baseline spec's scope to fix (this spec documents current behavior, it does not correct the underlying data file).
2. Whether `/security/alerts/` currently paginates, limits alert count, or has any filtering is not documented anywhere in project notes reviewed this session. **Needs verification:** check once Azure access is stable (ties to Task Breakdown Batch 3).

## 10. Traceability

This baseline is the **implicit foundation** for the 3 Group A forward-looking specs in `docs/specs/README.md` (Evidence-Linked ATT&CK Mapping, Sentinel Rules Validation Trail, Evidence-Chain PlantUML Diagrams) — all three extend behavior first documented here. **Important maintenance note:** once the Evidence-Linked ATT&CK Mapping spec is implemented (adding the `evidence` array to `attack_data.json`), this baseline's section 4 (Data Model) will need a corresponding update — the schema described here will become outdated the moment that spec ships. This is the first real test of whether Tier 2 (Spec-Anchored) discipline is sustained in this project: **update this file when that happens, don't let it silently drift.**

Not dependent on and does not affect the IOC Reputation Lookup or SECURITY.md Honest Limitations specs (different code paths, no shared data model).

## Revision Log

| Date | Change | Reason |
|---|---|---|
| 28.07.2026 | Initial baseline created, retroactively documenting the already-implemented Security Dashboard as the project's first Tier 2 (Spec-Anchored) pilot | Chosen as the pilot subsystem for retroactively spec-anchoring already-built work, given its direct connection to the 3 Group A forward-looking specs already written this session |
| 28.07.2026 (b) | Verification Batch 4 completed: Data Model (section 4) corrected to the real nested schema; REQ-08 corrected from "6/8/1/5" to the verified real counts "6/5/1/8"; Open Question 1 resolved; Acceptance Criteria updated to reflect actual verification status | Direct read of the live `attack_data.json` file surfaced that the project's long-standing status-count claim (6 mitigated/8 detected/1 monitored/5 gap) was stale — the real file shows 6/5/1/8, with 3 previously-uncounted gap techniques (T1068, T1110.004, T1528) tied to the KBSSE/RiskScoringMiddleware finding. This is the strongest "verify-before-lock" catch of the session, directly validating the purpose of this baseline pilot. |