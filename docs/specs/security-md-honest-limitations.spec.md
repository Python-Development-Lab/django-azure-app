# Spec: SECURITY.md "Honest Limitations" Section

**Status:** Draft
**Feature ID:** SEC-DOCS-HONEST-LIMITATIONS-01
**Related backlog item:** SECURITY.md (CRA Annex I VDP) — existing backlog item, refined 28.07.2026 to explicitly include an "Honest Limitations" section
**Owner:** Vitalii Shevchuk
**Target surface:** `SECURITY.md` (repository root)

---

## 1. Overview

Add an explicit "Honest Limitations" section to `SECURITY.md`, alongside the standard vulnerability-disclosure-policy (VDP) content required for CRA Annex I. This section aggregates and cross-references already-documented, real gaps in the project's security posture — it does not perform new gap analysis; it makes existing findings visible in the one file GitHub surfaces prominently for security-related discussions.

## 2. Problem Statement

`SECURITY.md` as conventionally used describes only how to report a vulnerability and which versions are supported — an asymmetric picture that says nothing about what the system does *not* protect against. This project already has substantial, well-documented gap analysis scattered across several places (`attack_data.json`'s 5 gap techniques, 16 failed MCSB regulatory controls from the 25.07.2026 session, the Critical Attack Path finding from 27.07.2026, RBAC over-privilege findings from 25.07.2026/27.07.2026) — none of which is currently visible in `SECURITY.md` itself. Consolidating references to these findings in one place is a low-cost, high-credibility addition for both portfolio/certification purposes and genuine transparency.

## 3. Scope

**In scope:**
- Standard `SECURITY.md` sections satisfying CRA Annex I VDP requirements (Reporting a Vulnerability, Supported Versions)
- A new "Honest Limitations" section aggregating references to already-documented findings only

**Out of scope (explicitly deferred):**
- Performing new security gap analysis — this spec only aggregates and cross-references existing, dated findings
- The full MCSB cross-reference document (`docs/compliance/mcsb-cross-reference.md`) — tracked as its own, separate backlog item; this spec references the raw 25.07.2026 session findings directly and can be refined to point at that document once it exists
- A live, auto-updating limitations feed — this is a manually maintained, periodically reviewed static document, consistent with the project's existing documentation practices (ADRs, compliance docs)

## 4. Data Model

**`SECURITY.md` structure:**

```
SECURITY.md
  1. Reporting a Vulnerability          (standard VDP content)
  2. Supported Versions                 (standard content)
  3. Honest Limitations                 (new)
     3a. Known ATT&CK Gap Techniques
     3b. Known Regulatory Compliance Gaps
     3c. Known Active Risks
     3d. Known Privilege Over-Scoping
     3e. Shared Responsibility Note
     3f. Resolved Limitations           (populated over time, per REQ-03)
```

**Subsection content sources (each entry must cite one of these):**

| Subsection | Source | Example content |
|---|---|---|
| 3a | `security/mitre/attack_data.json` (`gap` status entries) | T1027, T1530, T1486, T1531, T1595 |
| 3b | 25.07.2026 session — Azure Defender for Cloud Regulatory Compliance API, MCSB standard | 16 of 85 controls failed; category summary, not full detail |
| 3c | 27.07.2026 session — Defender for Cloud Attack Path Analysis | Critical attack path finding; remediation status (see Open Question 2 on disclosure detail) |
| 3d | 25.07.2026 session — manual RBAC review, corroborated by 27.07.2026 Azure CSPM assessment export | `django-azure-sp` subscription-scope Contributor + User Access Administrator; human admin Owner without PIM |
| 3e | `docs/compliance/azure-platform-certifications.md` | Cross-reference only, no restatement |

## 5. Requirements (EARS notation)

### 5.1 Structure and sourcing discipline

- **REQ-01 (Ubiquitous):** `SECURITY.md` shall contain a "Honest Limitations" section clearly separated from and visually distinguished from the standard vulnerability-disclosure-policy content.
- **REQ-02 (Ubiquitous):** Every entry listed under "Honest Limitations" shall cite an already-existing, dated finding or source document (per the table in section 4) — no entry shall present a new, previously undocumented claim.
- **REQ-07 (Ubiquitous):** The standard `SECURITY.md` sections (Reporting a Vulnerability, Supported Versions) shall satisfy CRA Annex I vulnerability-disclosure-policy requirements, per the original purpose of this backlog item.

### 5.2 Lifecycle of limitations

- **REQ-03 (Unwanted behavior):** If a documented limitation is subsequently remediated (e.g., the outdated cryptography package is updated, the over-scoped RBAC role assignments are narrowed), then the entry shall be moved to the "Resolved Limitations" subsection with a resolution date recorded, rather than silently deleted — mirroring the evidence-retention principle already established in the Evidence-Linked ATT&CK Mapping spec (REQ-12, `remediated_date`).
- **REQ-04 (Event-driven):** When a new significant gap is discovered in future work (e.g., a future MCSB scan, a new Defender Attack Path finding, a new manual review), it shall be added to this section following the same cite-the-source pattern established here, rather than being left documented only in a backlog item or session note with no visibility in `SECURITY.md` itself.

### 5.3 Shared responsibility framing

- **REQ-05 (Ubiquitous):** The "Honest Limitations" section shall explicitly distinguish gaps that are this project's responsibility (application code, IaC configuration, RBAC assignments) from gaps or assurances that belong to the underlying Azure platform, cross-referencing `docs/compliance/azure-platform-certifications.md` rather than restating its shared-responsibility argument.
- **REQ-06 (Optional feature):** Where a limitation corresponds to an ISO 27001 A.8.x finding already documented elsewhere in `docs/compliance/`, the entry shall reference that document by name rather than duplicating its content in `SECURITY.md`.

## 6. Non-Functional Requirements

- **NFR-01:** This is a pure documentation task — no code, Terraform, or Azure resource changes; no dependency on Azure write access.
- **NFR-02:** This spec does not require the separate `docs/compliance/mcsb-cross-reference.md` document to exist first — it may reference the raw 25.07.2026 session findings directly, and can be refined to point at that document once it is written.
- **NFR-03:** Each "Honest Limitations" entry shall be concise (a few sentences) with a reference/link to fuller detail elsewhere, rather than restating full compliance-report-level detail inline — `SECURITY.md` should stay a readable, scannable document, not a duplicate of the compliance documentation.

## 7. Task Breakdown

**Why this section exists:** batching requirements avoids handing an AI coding agent a dozen-plus requirements in one shot, which risks context rot (see `docs/specs/TEMPLATE.md` section 7 for the full rationale). Each batch below is sized for a single fresh Claude Code session.

| Batch | REQs covered | Description | Depends on | Azure write required? |
|---|---|---|---|---|
| 1 | REQ-01, REQ-02, REQ-07 | Standard `SECURITY.md` sections (VDP, Supported Versions) + Honest Limitations section skeleton | - | No |
| 2 | REQ-05, REQ-06 | Shared-responsibility framing + ISO 27001 / compliance-doc cross-references | Batch 1 | No |
| 3 | REQ-03, REQ-04 | "Resolved Limitations" subsection + process for adding future gaps | Batch 1 | No |

## 8. Acceptance Criteria (checklist)

- [ ] `SECURITY.md` exists at repository root with standard "Reporting a Vulnerability" and "Supported Versions" sections satisfying CRA Annex I intent
- [ ] "Honest Limitations" section present with all subsections outlined in section 4 (3a through 3f)
- [ ] Every entry in the section cites a specific, dated source (session date or document path) rather than an unsourced claim
- [ ] The shared-responsibility distinction (REQ-05) is explicit and cross-references `docs/compliance/azure-platform-certifications.md` rather than restating it
- [ ] No entry duplicates full MCSB or ISO 27001 compliance-report detail — references only, per NFR-03
- [ ] The Critical Attack Path entry (3c) follows the disclosure-detail decision made in Open Question 2 below

## 9. Open Questions

1. Whether to include the currently unresolved Azure subscription billing incident (`Auto pay failed`, `ReadOnlyDisabledSubscription`) as a limitation. **Recommendation: do not include it.** This is an account-administration/billing issue, not a limitation of the application's or infrastructure's security posture — it is out of scope for a security-disclosure document and would confuse readers about what `SECURITY.md` is meant to communicate.

2. Whether the Critical Attack Path entry (3c) should name specific exploit-enabling details (the exact outdated package, the precise attack chain, the Defender Attack Path ID) in a file that is publicly visible on GitHub, given the underlying vulnerability is not yet remediated as of this spec's authoring date. **Recommendation:** describe the gap category and remediation status without naming the specific vulnerable package or exact exploit chain until remediation is complete — e.g., "An outdated cryptographic dependency was identified via automated attack path analysis in July 2026, creating a potential lateral-movement path to a critical secrets store; remediation is in progress" rather than naming the package, CVE identifiers, or exact resource names. Once remediated, the entry can move to "Resolved Limitations" (per REQ-03) with full technical detail, since the risk of publishing exploit-enabling specifics no longer applies after the fix is deployed.

## 10. Traceability

This spec depends on findings already recorded from prior sessions: the 25.07.2026 MCSB regulatory compliance review, the 25.07.2026 and 27.07.2026 RBAC over-privilege findings (manual review and independent CSPM confirmation), and the 27.07.2026 Critical Attack Path discovery. It cross-references `docs/compliance/azure-platform-certifications.md` (shared responsibility mapping) and anticipates the still-unwritten `docs/compliance/mcsb-cross-reference.md`. It is independent of the three other specs from this session (Evidence-Linked ATT&CK Mapping, Sentinel Rules Validation Trail, Evidence-Chain PlantUML Diagrams) — no shared data model — though all four specs draw on the same underlying set of real findings from this project's July 2026 sessions, and should be kept mutually consistent on dates and technical facts where they describe the same incidents.
## Revision Log

| Date | Change | Reason |
|---|---|---|
| 28.07.2026 | Initial draft created, including the disclosure-detail decision in Open Question 2 from the outset | Authored after the Critical Attack Path finding was already known in the same session, prompting explicit consideration of what level of exploit detail is safe to publish in a public `SECURITY.md` before remediation is complete |
