# Spec: Spec-Driven Development Methodology — Baseline (Retroactive)

**Status:** Implemented
**Feature ID:** `SEC-RND-SDDMETHOD-01`
**Related backlog item:** N/A — this is retroactive documentation of the project's own development methodology, adopted 28.07.2026, formalized into this spec the same day
**Owner:** Vitalii Shevchuk
**Target surface:** `docs/specs/TEMPLATE.md`, `docs/specs/README.md`, `docs/backlog-status.md`, `docs/research-notes.md`, `.claude/agents/security-reviewer.md`

---

## 1. Overview

This spec retroactively documents the **already-adopted, already-in-use** Spec-Driven Development methodology for this project — the second Tier 2 (Spec-Anchored) baseline in this project, alongside `security-dashboard-baseline.spec.md`. It is **not** a design document for new process: it captures the methodology as it exists after producing 8 specs in one session, so that (a) future sessions can check new specs against a known-good baseline rather than reconstructing the discipline from memory, and (b) the methodology's own real gaps (identified during its use) are recorded as Open Questions rather than lost.

## 2. Problem Statement

Before 28.07.2026, this project had no formal spec process — backlog items lived as prose in memory. Once adopted, the methodology itself (template structure, EARS notation, Task Breakdown, Traceability Verification, Revision Log, a verify-before-lock discipline, three persistent trackers) was built up **incrementally and ad-hoc** across one long session — never itself specified as a coherent, testable system. This creates the same risk any undocumented subsystem has: a future session could silently drift from the established discipline (skip a verify-before-lock check, forget to update a tracker, blend Task Breakdown into the wrong section) with no baseline to catch the drift against.

## 3. Scope

**In scope:**
- Documenting the existing 10-section spec structure + Revision Log + Requirement Traceability Verification (per `docs/specs/TEMPLATE.md`)
- Documenting the existing EARS notation convention (5 patterns, sequential numbering)
- Documenting the existing verify-before-lock discipline, evidenced by 5 real corrections made this session
- Documenting the existing Task Breakdown practice (batching for context-rot mitigation)
- Documenting the existing three persistent trackers (`backlog-status.md`, `docs/specs/README.md`, `docs/research-notes.md`)
- Documenting the existing retroactive-baseline pattern itself (this spec is an instance of it)

**Out of scope (explicitly deferred — these are identified gaps, not part of what's already adopted):**
- A formal "Explore" step as a mandatory, enforced pre-spec-authoring action (currently only a Usage Note recommendation in `TEMPLATE.md`, not yet a REQ — see Open Question 2)
- A separate, formalized "Clarify" pass distinct from writing Open Questions inline (currently blended into one authoring pass)
- Any numeric quality gate (e.g., a Clarity Score) before a spec can move from Draft to "ready for implementation"
- Automating `docs/research-notes.md` population or building a real `research-cache.md`-style system beyond manual entry
- Any CI/tooling enforcement of tracker consistency (e.g., a check that `README.md`'s spec count matches `docs/specs/*.spec.md`'s actual file count) — currently manual discipline only

## 4. Data Model

The methodology's "data model" is the set of file/section structures it prescribes, not a JSON schema:

- **Spec file structure** (`docs/specs/TEMPLATE.md`): 10 numbered sections (Overview, Problem Statement, Scope, Data Model, Requirements [EARS], Non-Functional Requirements, Task Breakdown, Acceptance Criteria, Open Questions, Traceability) + an unnumbered Revision Log + an unnumbered, post-implementation-only Requirement Traceability Verification table.
- **EARS requirement format**: `**REQ-NN (Pattern):** <statement>`, where Pattern is one of Ubiquitous / Event-driven / State-driven / Unwanted behavior / Optional feature, and NN is sequential across the whole document (not restarted per subsection).
- **Task Breakdown table columns**: Batch | REQs covered | Description | Depends on | Azure write required?
- **Revision Log table columns**: Date | Change | Reason
- **Requirement Traceability Verification table columns**: REQ | Status (satisfied/partially satisfied/missing) | Implementation (file:symbol) | Test/Verification | Notes
- **`docs/specs/README.md` index columns**: # | Spec File | Feature ID | Status | Depends On | Azure Blocker | Revisions
- **`docs/backlog-status.md` row columns**: Item | Spec | Blocker | Priority | Source

## 5. Requirements (EARS notation) — describing existing, established practice

### 5.1 Spec authoring structure

- **REQ-01 (Ubiquitous):** Every spec authored for this project shall follow the 10-section structure defined in `docs/specs/TEMPLATE.md`, plus a Revision Log.
- **REQ-02 (Ubiquitous):** Every requirement within a spec shall be written using one of the 5 EARS patterns and numbered sequentially (REQ-01, REQ-02, ...) across the whole document, not restarted per subsection.

### 5.2 Verification discipline ("verify-before-lock")

- **REQ-03 (Unwanted behavior):** If a spec's Problem Statement, Data Model, or Requirements section makes a factual claim about existing code, data, or infrastructure, then that claim shall be verified against the live system before the spec is treated as ready for implementation — not asserted from memory or inference alone.
- **REQ-04 (Event-driven):** When a verification check reveals that an earlier assumption in a spec was incorrect, the spec author shall correct the spec's affected sections and record the correction in its Revision Log — never silently edit without a trace.

### 5.3 Task decomposition

- **REQ-05 (Ubiquitous):** Every spec's requirements shall be grouped into a Task Breakdown table (batches of roughly 3-6 requirements each) before being handed to an AI coding agent for implementation, to mitigate context-rot risk from over-large single requests.
- **REQ-06 (Optional feature):** Where a spec has fewer than ~6 total requirements, a single batch is acceptable — the Task Breakdown table is still present, but not artificially split for its own sake.

### 5.4 Post-implementation verification

- **REQ-07 (Event-driven):** When a spec's implementation is complete, an independent verification pass (ideally run in a fresh agent session, not the one that wrote the implementation) shall populate the spec's Requirement Traceability Verification table before the spec's Status field is changed from Draft to Implemented.

### 5.5 Persistent memory / cross-session tracking

- **REQ-08 (Ubiquitous):** The project shall maintain three persistent tracking artifacts — `docs/backlog-status.md` (all backlog items + spec/blocker status + Metrics), `docs/specs/README.md` (index of all specs + implementation order + revision notes), and `docs/research-notes.md` (registry of external sources reviewed) — kept current whenever a spec is authored, revised, or a new external source is researched.
- **REQ-09 (Unwanted behavior):** If a new spec or backlog change is made without updating the corresponding tracker, then this is a methodology violation to be corrected in the same session or the very next one — not deferred indefinitely.

### 5.6 Retroactive baselining (the Tier 2 pilot pattern)

- **REQ-10 (Optional feature):** Where an already-built, undocumented subsystem or process is judged valuable to formally document, a retroactive "baseline" spec (Status: `Implemented` from creation) may be authored following the same 10-section structure, with its Task Breakdown reframed as "Verification Batches" rather than build batches.

## 6. Non-Functional Requirements

- **NFR-01:** This methodology requires no Azure resources or write access — it is pure process/documentation discipline, fully exercisable during the current Azure billing block.
- **NFR-02:** Adopting and maintaining this methodology has a real, non-zero time cost (writing 10 sections, Task Breakdown tables, trackers) — this is accepted as justified given the concrete verify-before-lock catches already demonstrated (see `docs/backlog-status.md`'s Metrics section), not treated as free.

## 7. Task Breakdown (Verification Batches)

**Why "verification" rather than "implementation":** like `security-dashboard-baseline.spec.md`, this spec documents already-existing practice. The batches below check that the spec accurately describes real, current behavior.

| Batch | REQs covered | Verification action | Depends on | Azure access required? |
|---|---|---|---|---|
| 1 | REQ-01, REQ-02 | Check all 8 existing specs in `docs/specs/` against the 10-section structure and EARS numbering convention | - | No |
| 2 | REQ-03, REQ-04 | Cross-reference the 5 documented verify-before-lock corrections in `docs/backlog-status.md`'s Metrics section against each spec's own Revision Log | - | No |
| 3 | REQ-05, REQ-06 | Confirm all 8 specs have a populated Task Breakdown table with reasonable batch sizes | - | No |
| 4 | REQ-07 | Check whether any spec's Requirement Traceability Verification table has been populated yet | - | No |
| 5 | REQ-08, REQ-09 | Confirm all 3 trackers exist, and spot-check their content against the actual current state of `docs/specs/` | - | No |
| 6 | REQ-10 | Confirm `security-dashboard-baseline.spec.md` correctly follows the retroactive-baseline pattern this REQ describes | - | No |

## 8. Acceptance Criteria (checklist)

- [x] All 8 existing specs follow the 10-section + Revision Log structure (REQ-01) — confirmed by direct inspection at authoring time
- [x] EARS notation used consistently, sequential numbering across each document (REQ-02)
- [x] At least 5 documented verify-before-lock corrections exist and are cross-referenced in `docs/backlog-status.md`'s Metrics section (REQ-03/REQ-04)
- [x] All 8 specs have a populated Task Breakdown table (REQ-05/REQ-06)
- [ ] **REQ-07 has not yet been exercised in practice** — every spec's Requirement Traceability Verification table is still an empty placeholder, since no spec has been implemented yet (all 6 forward-looking Draft specs remain unimplemented as of this baseline's authoring date)
- [x] 3 trackers exist and were updated multiple times this session (REQ-08)
- [x] Retroactive baseline pattern established and applied once already (REQ-10 — `security-dashboard-baseline.spec.md`)

## 9. Open Questions

1. Whether REQ-09 (methodology-violation correction) needs a more formal enforcement mechanism (e.g., a CI check comparing `README.md`'s spec count against the actual file count in `docs/specs/`) versus remaining manual discipline. **Recommendation:** manual discipline is sufficient at the current scale (8 specs) — revisit only if the spec count grows significantly or a real drift incident occurs (the missing "## Summary Counts" header found and fixed in `backlog-status.md` during this same session is a small example of the kind of drift this would catch, but was caught manually without difficulty).
2. Whether to promote the "run an Explore step before implementing any spec" recommendation — currently only a Usage Note in `TEMPLATE.md` — into a formal REQ in a future revision of this spec. This has already been identified as this methodology's single biggest actionable gap (see `docs/research-notes.md`'s summary of the Yazidi article review). **Recommendation:** promote it to REQ-11 in this spec's next revision, once the Explore step has actually been exercised at least once in practice — don't formalize a requirement that hasn't yet been tested.

## 10. Traceability

This spec is **meta** relative to the other 8 specs in `docs/specs/README.md` — it describes the process all of them follow, rather than sharing a data model or implementation dependency with any single one. It documents: `docs/specs/TEMPLATE.md` (the structure), `docs/specs/README.md` (tracker #1), `docs/backlog-status.md` (tracker #2, including its Metrics section), `docs/research-notes.md` (tracker #3), and `.claude/agents/security-reviewer.md` (a designed-but-not-yet-exercised component of REQ-07's independent-verification intent). It is directly analogous in structure and purpose to `security-dashboard-baseline.spec.md` — both are Tier 2 retroactive baselines using "Verification Batches"; this one documents the project's development process rather than an application subsystem.

**Critical maintenance risk (same pattern as the Security Dashboard baseline):** if the methodology evolves — e.g., Open Question 2 is resolved and a new REQ-11 is added — this spec must be updated in the same change, or it will itself become the kind of stale, confidently-wrong documentation this whole methodology exists to prevent.

## Revision Log

| Date | Change | Reason |
|---|---|---|
| 28.07.2026 | Initial baseline created, retroactively documenting the already-adopted SDD methodology as the project's second Tier 2 (Spec-Anchored) pilot | The methodology itself was built up ad-hoc across one long session and had never been formally specified as its own system — this closes that gap, following the same retroactive-baseline pattern (REQ-10) it documents |

---

## Requirement Traceability Verification

*(Not applicable in the usual post-implementation sense — this baseline documents already-existing, already-"implemented" practice from its creation. See section 8's Acceptance Criteria checklist for the equivalent verification status instead.)*