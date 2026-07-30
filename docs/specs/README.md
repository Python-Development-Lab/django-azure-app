# Specs Index

**Purpose:** Single index of all formal SDD spec files in `docs/specs/`, tracking implementation status, inter-spec dependencies, and Azure-access requirements — consolidating information otherwise scattered across each spec's own Traceability and Revision Log sections.

**Last updated:** 28.07.2026

**Status legend:**
- **Draft** — spec written and internally consistent (all Open Questions resolved), not yet implemented
- **In Progress** — implementation started (code/config changes underway), spec may still be revised based on implementation findings
- **Implemented** — feature shipped, acceptance criteria verified, spec is now a historical record of what was built and why

---

## Index

| # | Spec File | Feature ID | Status | Depends On | Azure Blocker | Revisions |
|---|---|---|---|---|---|---|
| 1 | [`evidence-linked-attack-mapping.spec.md`](./evidence-linked-attack-mapping.spec.md) | `SEC-DASH-EVIDENCE-01` | Draft | None | docs-only | 3 |
| 2 | [`sentinel-rules-validation-trail.spec.md`](./sentinel-rules-validation-trail.spec.md) | `SEC-DASH-VALIDATION-01` | Draft | None (shares incident data with #1, see below) | docs-only | 1 |
| 3 | [`evidence-chain-plantuml-diagrams.spec.md`](./evidence-chain-plantuml-diagrams.spec.md) | `SEC-DASH-DIAGRAMS-01` | Draft | **#1 and #2** (must be implemented first — see Implementation Order) | docs-only | 1 |
| 4 | [`ioc-reputation-lookup.spec.md`](./ioc-reputation-lookup.spec.md) | `SEC-DASH-IOC-01` | Draft | None | mixed (spec/code writable now; live test against `/security/alerts/` requires Azure) | 3 |
| 5 | [`security-md-honest-limitations.spec.md`](./security-md-honest-limitations.spec.md) | `SEC-DOCS-HONEST-LIMITATIONS-01` | Draft | References facts from #1–#3 and `docs/compliance/azure-platform-certifications.md` (factual consistency only, not a data-model dependency) | docs-only | 1 |
| 6 | [`security-dashboard-baseline.spec.md`](./security-dashboard-baseline.spec.md) | `SEC-DASH-BASELINE-01` | **Implemented** (retroactive) | N/A — see Baseline Specs section below | docs-only | 2 |
| 7 | [`ask-ai-alert-panel.spec.md`](./ask-ai-alert-panel.spec.md) | `SEC-DASH-ASKAI-01` | Draft | None (sole source of truth is `docs/threat-models/0001-ask-ai-alert-panel.md`, not another spec — see Traceability) | mixed (Key Vault secret for Claude API key is the only Azure touch) | 1 |
| 8 | [`security-investment-cost-effectiveness-model.spec.md`](./security-investment-cost-effectiveness-model.spec.md) | `SEC-RND-COSTMODEL-01` | Draft | None — reads live FinOps + Secure Score data, no dependency on other specs (REQ-07 optionally references Spec #1's `evidence` array once it ships) | docs-only (read-only Azure API queries) | 1 |
| 9 | [`sdd-methodology-baseline.spec.md`](./sdd-methodology-baseline.spec.md) | `SEC-RND-SDDMETHOD-01` | **Implemented** (retroactive) | None — meta-spec describing the project's own development process, not any single feature spec | docs-only | 1 |
| 10 | [`sdd-case-study-article.spec.md`](./sdd-case-study-article.spec.md) | `SEC-RND-CASESTUDY-01` | Draft | Sources content from Specs #1-#9's Revision Logs + `docs/backlog-status.md` Metrics + `docs/research-notes.md` (factual sourcing only, not a code/data-model dependency) | docs-only | 1 |

## Implementation Order

Two independent groups, ordered internally where dependencies exist:

**Group A — Security Dashboard evidence chain (implement #1 and #2 before #3):**
```
1. Evidence-Linked ATT&CK Mapping   ─┐
2. Sentinel Rules Validation Trail ─┴──► 3. Evidence-Chain PlantUML Diagrams
```
Spec #3 explicitly states it should be implemented last among this group — it visualizes facts recorded in #1 and #2, and implementing it first risks diagrams drifting from not-yet-finalized evidence/validation content.

**Group B — Independent (implement in any order, at any time):**
```
4. IOC Reputation Lookup
5. SECURITY.md Honest Limitations
7. Ask AI About This Alert Panel
```
Spec #5 references facts established in Group A (incident dates, technique IDs) for consistency, but has no code-level or data-model dependency — it can be drafted and refined in parallel with Group A's implementation, as long as incident details are kept in sync. Spec #7 is similarly independent for implementation, but its *content* is entirely sourced from `docs/threat-models/0001-ask-ai-alert-panel.md` rather than from any other spec in this index — see Traceability in that file.

**Group C — R&D / Methodology (independent, exploratory, not a Security Dashboard feature):**
```
8. Security Investment Cost-Effectiveness Model
9. SDD Methodology Baseline (retroactive, internal process contract)
10. SDD Case-Study Article (external-facing narrative, sources from #1-#9)
```
Spec #8 is categorically different from Groups A and B: it does not describe a feature to build into the application — it describes a **research methodology** for correlating this project's FinOps cost data with Secure Score impact, producing a periodic analyst-run report rather than live dashboard code. It optionally references Spec #1's `evidence` array (REQ-07) once that ships, but has no hard dependency on it.

Spec #9 is a second Tier 2 retroactive baseline (alongside Spec #6), but for the *development process itself* rather than an application subsystem — it documents the spec-authoring/verification/tracking discipline already in use as of 28.07.2026.

Spec #10 is distinct from Spec #9: where #9 is an internal EARS process-contract, #10 specifies requirements for an *external-facing narrative article* about this project's SDD adoption experience (portfolio/career content). They share source material (the project's Revision Logs and Metrics) but serve different audiences and must not be merged into one document.

## Baseline Specs (Retroactive, Tier 2 Pilot)

Spec #6 is fundamentally different from Specs #1–#5: it does not describe future work. It **retroactively documents already-built, already-working functionality** (the Security Dashboard, built pre-SDD in June–July 2026) as a formal EARS contract — the project's first pilot of Tier 2 (Spec-Anchored) discipline, where a spec is kept in sync with existing code rather than preceding new code.

It is **not part of the forward Implementation Order** above — there is nothing to "implement," only to periodically re-verify (see its own Task Breakdown, framed as Verification Batches rather than build batches).

**Critical maintenance risk specific to this spec:** Spec #6's Data Model section describes the *current* (pre-implementation) shape of `attack_data.json`. Once Spec #1 (Evidence-Linked ATT&CK Mapping) is implemented and adds the `evidence` array to that file, Spec #6 will describe a stale schema unless it is updated at the same time. This is the first real test of whether Tier 2 discipline holds in this project — **when Spec #1 ships, update Spec #6's section 4 in the same commit or the next one, don't let it silently drift.**

Whether other subsystems (FinOps Dashboard, CI/CD pipeline, Terraform modules) get the same retroactive baseline treatment is an open decision — deferred until this pilot proves its value in practice.

## Revision Notes (see each file's own Revision Log for full detail)

- **Spec #1** was revised twice: once after direct portal inspection confirmed the exact MITRE ATT&CK technique IDs for the Critical Attack Path (replacing a placeholder), and again — more significantly — after direct verification of the live `attack_data.json` file revealed its entire Data Model section had assumed the wrong schema (flat `technique_id` field vs. the real nested `tactics[].techniques[].id` structure), plus a real status conflict (`T1552`) and missing entries (`TA0008`, `T1021`, `T1021.007`, `T1555.005`) not discoverable without reading the live file.
- **Spec #4** is independently the most-revised spec in this set (2 revisions after the initial draft) — its first revision incorrectly deprioritized the primary data source after querying a deprecated legacy Azure table; a follow-up check against the correct table reversed that decision. This is the clearest example in the project of the "verify-before-lock" cycle: draft → check assumption against real data → correct the spec accordingly.
- **Specs #2, #3, #5** were each authored complete in a single pass, since the real findings they depend on (the Critical Attack Path, its 4 technique IDs) were already confirmed earlier in the same session — no post-hoc revision was needed.
- **Spec #6** was revised once, correcting REQ-08's status-count claim (project-wide "6/8/1/5" was stale; the real file showed "6/5/1/8") after its own Verification Batch 4 was actually run — the strongest validation yet that the baseline-pilot concept works as intended.
- **Spec #7** is unique among specs #1-#7: it is the only one sourced entirely from a **pre-existing artifact** (`docs/threat-models/0001-ask-ai-alert-panel.md`, dated 25.07.2026) rather than from this session's own analysis — discovered during the Security Dashboard baseline's verification pass, not planned in advance.
- **Spec #8** is unique in a different way: it is the only spec explicitly built **around correcting a same-session error** — an unverified claim (that fixing `cryptography` would raise Secure Score from 36% to ~67%) was made, then found via direct API verification to likely be misattributed to a different project (`hornetdashboardprod`) sharing the same Azure subscription. REQ-01/REQ-02 exist specifically to prevent that class of mistake going forward.
- **Spec #9** documents the methodology all 9 (now 10) specs in this index actually follow — it is `Implemented` from creation, like Spec #6, since it captures already-adopted practice rather than proposing new process. Its own Acceptance Criteria honestly notes that REQ-07 (post-implementation Traceability Verification) has never actually been exercised yet, since no forward-looking spec has been implemented as of this spec's authoring date.
- **Spec #10** was authored after some back-and-forth about what "an R&D artifact for the SDD methodology" should actually mean — the session initially produced an internal process-spec (#9), then a freeform narrative article, then this formal EARS spec *about* that article, before settling on keeping all three as distinct, related artifacts rather than merging them. Recorded here as a real example of the kind of scope confusion this project's own documentation discipline is meant to catch and resolve, not hide.

## Related Documents (not specs, but closely tied to this index)

| Document | Relationship |
|---|---|
| `docs/backlog-status.md` | Broader backlog view (46 items total); tracks which items have a spec here versus which are still unspecified |
| `docs/compliance/reference/azure-platform-certifications.md` | Shared-responsibility reference cited by Spec #5 — **note:** moved from `docs/compliance/` to `docs/compliance/reference/` on 28.07.2026 after it was found to risk corrupting the live `security_compliance` panel's control count; this table previously cited the stale pre-move path |
| `docs/security/rule-validation/` (to be created per Spec #2) | Output of implementing Spec #2 |
| `docs/diagrams/evidence-chain-*.puml` (to be created per Spec #3) | Output of implementing Spec #3 |
| `security/mitre/attack_data.json` | The live file Spec #6 documents the current schema of — must be re-diffed against Spec #6 section 4 whenever this file's schema changes |
| `docs/threat-models/0001-ask-ai-alert-panel.md` | Sole source of truth for Spec #7 — keep both in sync; do not let this pre-existing threat model and the derived EARS spec drift apart |
| `docs/playbooks/T1110-http-brute-force.md` | Real, pre-existing incident-response playbook — candidate source for a future "Automated Response Gap" spec, not yet written |
| `docs/research/security-cost-effectiveness-model.md` (to be created per Spec #8) | Output of implementing Spec #8 — the actual methodology report and ranked output, distinct from the spec itself |
| `docs/writing/sdd-security-compliance-case-study.md` | Output of Spec #10 — the actual case-study article, already drafted and self-verified (see Spec #10's Revision Log) |
| `docs/specs/CONSTITUTION.md` | Persistent, non-negotiable project rules (Azure identity/secrets, Terraform, security-claims integrity, compliance format, SDD process, scope discipline) — inspired by GitHub Spec Kit's `constitution.md` concept (see `docs/research-notes.md`), adopted standalone rather than the full toolchain. Every spec should be checked against this file, not the other way around. |

## Maintenance Note

Update this index whenever:
1. A spec's status changes (Draft → In Progress → Implemented) — update the Status column.
2. A spec is revised — update the Revisions count here and add the detail to that spec's own Revision Log.
3. A new spec is authored — add a new row, and update Implementation Order if it has dependencies on existing specs.
4. A spec is implemented — as of Spec #6, this index now contains one Implemented spec; revisit whether a dedicated "Implemented" table section is worth splitting out once more specs reach that status, rather than mixing Draft and Implemented rows in one table indefinitely.
5. A baseline (retroactive, "Implemented") spec's underlying data model or behavior changes because a forward-looking spec ships (e.g., Spec #1 adding the `evidence` array to `attack_data.json`) — update the baseline spec's affected section in the same change, per the Baseline Specs section above. This is not optional bookkeeping — a stale baseline spec is worse than no baseline spec, since it asserts confidently-wrong information.