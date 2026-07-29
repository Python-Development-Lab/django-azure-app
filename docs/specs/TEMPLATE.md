# Spec: [Feature Name]

**Status:** Draft
**Feature ID:** `[CATEGORY-AREA-NN]` — see naming convention below
**Related backlog item:** [date, source — e.g., "27.07.2026, from AdversaryGraph article comparison" or "long-standing project backlog"]
**Owner:** [name]
**Target surface:** [file(s)/directory this spec touches, e.g., `attack_data.json`, `templates/core/partials/x.html`]

---

## 1. Overview

[1-3 sentences: what this spec adds or changes, and the one-line reason it exists. State explicitly whether this is a documentation-only change, a code change, or requires live infrastructure — this determines whether it can be implemented while Azure write-access is blocked.]

## 2. Problem Statement

[What's missing or broken today, in concrete terms. Cite specific evidence — a real incident, a real finding, a real gap already documented elsewhere in the project — rather than a hypothetical problem. If there's no real, cite-able problem yet, the spec may be premature.]

## 3. Scope

**In scope:**
- [Bullet list — be specific about what this spec covers]

**Out of scope (explicitly deferred):**
- [Bullet list — name what's deliberately NOT being built, and why. This section is what prevents scope creep and over-engineering; every "no" here should have a one-clause justification.]

## 4. Data Model

[Any new fields, JSON schema additions, file structures, or data shapes this spec introduces. Use a code block for concrete examples. If no new data model is introduced, state that explicitly rather than omitting the section.]

## 5. Requirements (EARS notation)

**EARS quick reference** (delete this block once the spec author is comfortable with the patterns):

| Type | Template | Use for |
|---|---|---|
| Ubiquitous | The `<system>` shall `<response>` | Always-true behavior |
| Event-driven | When `<trigger>`, the `<system>` shall `<response>` | Behavior triggered by an event |
| State-driven | While `<state>`, the `<system>` shall `<response>` | Behavior conditional on an ongoing state |
| Unwanted behavior | If `<trigger>`, then the `<system>` shall `<response>` | Error handling, validation, guardrails |
| Optional feature | Where `<feature>`, the `<system>` shall `<response>` | Conditional/opt-in behavior |

### 5.1 [Sub-area name]

- **REQ-01 (Ubiquitous):** [...]
- **REQ-02 (Event-driven):** When [...], the system shall [...].

### 5.2 [Sub-area name]

- **REQ-0N (Unwanted behavior):** If [...], then the system shall [...].

[Add sub-sections as needed. Number requirements sequentially across the whole document (REQ-01, REQ-02, ...) rather than restarting per sub-section, so cross-references from other specs or later revisions stay unambiguous.]

## 6. Non-Functional Requirements

- **NFR-01:** [Performance, cost, infrastructure-footprint, or Azure-dependency constraints. Always state explicitly whether this spec requires Azure write access, and if so, exactly what — this feeds directly into `docs/backlog-status.md`'s blocker classification.]
- **NFR-02:** [...]

## 7. Task Breakdown

**Why this section exists:** handing an AI coding agent (e.g., Claude Code) a spec with a dozen-plus requirements in one go risks "context rot" — model performance degrades as input length grows, well before the nominal context-window limit is reached, and degrades further for information in the middle of a long context ("lost in the middle"). Grouping requirements into small, independently implementable batches — and giving each batch to a fresh session rather than accumulating everything into one long conversation — mitigates this. This mirrors the "atomic execution units that fit safely within a fresh context window" principle from spec-driven-development literature (see e.g. the AI-RPI and GSD frameworks' subagent-dispatch patterns).

**Batch table:**

| Batch | REQs covered | Description | Depends on | Azure write required? |
|---|---|---|---|---|
| 1 | REQ-01, REQ-0N | [Short description — e.g., "data schema + validation"] | — | No |
| 2 | REQ-0N–REQ-0N | [...] | Batch 1 | No / Yes |
| 3 | REQ-0N–REQ-0N | [...] | Batch 1, 2 | Yes |

**Guidance for filling this table:**
- Each batch should be small enough to implement, test, and review within a single fresh agent session — as a rule of thumb, prefer 3-6 requirements per batch over dumping 10+ into one.
- Order batches so that data-model/validation work comes before UI/visualization work, and docs-only work comes before anything requiring Azure write access (per NFR) — this lets implementation proceed as far as possible even while Azure access is blocked, consistent with `docs/backlog-status.md`'s docs-only/blocked-on-azure distinction.
- If a spec has fewer than ~6 requirements total, a single batch is fine — don't force artificial splitting for its own sake.

## 8. Acceptance Criteria (checklist)

- [ ] [One checkbox per testable outcome — should map close to 1:1 with the REQs above]
- [ ] [...]

## 9. Open Questions

[Number each open question. For each, either give a recommendation (if you have enough information to propose one) or explicitly state what needs to be checked before it can be answered. An open question with no recommendation and no path to resolution is a sign the spec was written prematurely — either resolve it before finalizing, or explicitly note what real-world check would resolve it.]

1. [Question] — **Recommendation:** [...] *(or)* **Needs verification:** [what to check, and how]

## 10. Traceability

[List every other spec, backlog item, or document this spec depends on or is depended on by. State the nature of the dependency explicitly (shared data model? factual consistency only? implementation ordering?) — vague "related to X" statements are not useful; say *what kind* of relationship it is. Update `docs/specs/README.md`'s Index and Implementation Order sections when this spec is added.]

## Revision Log

| Date | Change | Reason |
|---|---|---|
| [date] | Initial draft created | [why now — what prompted this spec] |

---

## Requirement Traceability Verification (fill in only after implementation)

**Do not populate this section while authoring the spec.** This is a separate, post-implementation verification pass — ideally run in a fresh agent session, not the same conversation that wrote the implementation, to avoid the self-review blind spot (an agent that just wrote code is biased toward believing it's correct). Green tests are necessary but not sufficient: a passing test suite can still hide a requirement that was quietly never implemented. Prompt used for this pass:

> Audit the completed implementation against `docs/specs/[this-file].spec.md`. Do not modify code during this pass. For every requirement REQ-01 through REQ-NN, provide: Status (satisfied / partially satisfied / missing), implementation file and symbol, test file and test name.

| REQ | Status | Implementation (file:symbol) | Test (file::test_name) | Notes |
|---|---|---|---|---|
| REQ-01 | — | — | — | — |
| REQ-02 | — | — | — | — |

Only change the spec's **Status** field (top of file) from `Draft` to `Implemented` once this table is fully populated and every requirement is `satisfied` (or any `partially satisfied`/`missing` entries have been explicitly accepted as known limitations, cross-referenced in Open Questions or a new SECURITY.md Honest Limitations entry rather than silently ignored).

---

## Usage Notes (delete this section when creating a real spec from this template)

**File naming:** `kebab-case-feature-name.spec.md`, placed in `docs/specs/`.

**Feature ID convention observed so far:** `[DOMAIN]-[AREA]-[NN]`, e.g. `SEC-DASH-EVIDENCE-01` (security dashboard area), `SEC-DOCS-HONEST-LIMITATIONS-01` (documentation area). Pick a short domain/area prefix consistent with existing IDs in `docs/specs/README.md` rather than inventing a new scheme per spec.

**Before finalizing a spec:**
1. Every Open Question should be either resolved (with the real check performed and the answer recorded) or have an explicit recommendation — don't leave a spec "ready for implementation" with unresolved blind guesses baked into the Requirements section.
2. Every claim in Problem Statement, Data Model, and Requirements should trace back to something real and already documented elsewhere in the project (an incident, a session finding, a prior spec) — do not invent hypothetical scenarios to justify a requirement.
3. Fill in the Task Breakdown table (section 7) — group requirements into batches sized for a single fresh agent session before handing the spec to Claude Code, rather than requesting all requirements in one long conversation.
4. **Before handing any batch to Claude Code, run an Explore step first** ("Explore [relevant files] without modifying anything. Confirm the current schema/conventions and report any discrepancy with this spec's Data Model/Requirements section.") — do not let Claude Code implement directly against a spec's assumptions without confirming them against the live codebase first. This is exactly the gap that surfaced in `security-dashboard-baseline.spec.md`'s Open Question 1.
5. Add the new spec to `docs/specs/README.md`'s Index table and Implementation Order section.
6. If the spec depends on or is depended on by another spec, cross-reference both directions (in this spec's Traceability, and by updating the other spec's Traceability if needed).

**After implementation:** populate the Requirement Traceability Verification table above (ideally in a fresh session — see `.claude/agents/security-reviewer.md` for a ready-made independent-review subagent) before changing Status to Implemented.

**After any post-creation revision:** add an entry to this spec's own Revision Log (date, what changed, why) — do not silently edit Requirements or Acceptance Criteria without a record. See `docs/specs/ioc-reputation-lookup.spec.md` for a real example of a spec that went through two corrective revisions, and why the log matters there.
