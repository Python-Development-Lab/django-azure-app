# Spec: SDD Case-Study Article (Security + Compliance Context)

**Status:** Draft
**Feature ID:** `SEC-RND-CASESTUDY-01`
**Related backlog item:** R&D direction #4, identified 28.07.2026 during project-goals reflection: "SDD-методологія цієї сесії як самостійний артефакт" — a differentiated methodological document, since most SDD content online is generic-software-focused, not security/compliance-specific
**Owner:** Vitalii Shevchuk
**Target surface:** a standalone article/document (e.g. `docs/writing/sdd-security-compliance-case-study.md`) — a documentation deliverable, not application code

---

## 1. Overview

Formalize the requirements for a case-study article documenting this project's real experience adopting Spec-Driven Development in a security-engineering + compliance context, intended as differentiated portfolio/career content (per this project's own Purpose #3 — career/portfolio artifact). A first draft of this article was produced the same day this spec was written (`docs/writing/sdd-security-compliance-case-study.md`) — this spec formalizes what that draft must satisfy and gives a checkable basis for revising it, rather than treating it as a one-off, unspecified piece of writing.

## 2. Problem Statement

This project ran a genuine, first-hand SDD adoption case study in a single session: 9 formal specs authored, 5 documented verify-before-lock corrections, 3 persistent tracking artifacts built, and a retroactive baseline pattern established for both an application subsystem and the methodology itself. Most publicly available SDD writing is generic-software-focused (CRUD APIs, stateful agents, SaaS features) — none of the sources already reviewed for this project (see `docs/research-notes.md`) address the specific failure mode this project encountered repeatedly: a wrong assumption in a security/compliance context doesn't just break a feature, it produces a false assurance claim (a wrong coverage count, a wrong control status, a wrong Secure Score attribution). This is genuinely differentiated content, but only if the article is held to the same sourcing/honesty discipline as the rest of this project's documentation — not written as an unverified highlight reel.

## 3. Scope

**In scope:**
- Content requirements for the article: what it must cover, how claims must be sourced, what honesty/limitations disclosure it must include
- Audience and differentiation requirements (explicitly security/compliance-literate readers, explicitly contrasted against generic SDD content already reviewed)
- A lightweight maintenance discipline (the article should be revised as new catches/specs occur, not frozen)

**Out of scope (explicitly deferred):**
- A full external-publishing pipeline (platform selection, SEO, promotion) — this spec covers content requirements only
- Translation into Ukrainian — the article targets an English-reading audience per this project's established English-for-technical-output convention; a Ukrainian version is a separate, optional future increment if ever needed
- Covering the full 44-item backlog as a general project retrospective — this article is scoped specifically to the SDD-adoption case study, not a broader project narrative

## 4. Data Model

Not applicable in a JSON-schema sense — the "data model" here is the required document structure:

1. A differentiation statement (why this isn't generic SDD content)
2. A brief project-context section (what the project is, why it matters that it already had live security/compliance artifacts)
3. A narrated account of each real verify-before-lock catch, with enough technical specificity to be credible (table names, real numbers, not vague generalities)
4. A section on what's uniquely different about doing SDD in a security/compliance domain versus generic software development
5. An honest-limitations section (see REQ-02)
6. A short, practical recommendations section for readers attempting something similar
7. A footer citing the actual project artifacts (specs, trackers) the article draws from

## 5. Requirements (EARS notation)

### 5.1 Content sourcing and honesty

- **REQ-01 (Ubiquitous):** Every specific technical claim in the article (a catch, a metric, a number) shall be traceable to an existing project artifact — a spec's Revision Log, `docs/backlog-status.md`'s Metrics section, or `docs/research-notes.md` — no invented or embellished details.
- **REQ-02 (Ubiquitous):** The article shall include an explicit "honest limitations" section acknowledging what the methodology has *not yet* accomplished (e.g., no forward-looking spec implemented yet, the Dependabot warning left unexamined, the "Explore" step not yet formalized) — mirroring this project's own `security-md-honest-limitations.spec.md` principle, applied reflexively to the article about the methodology itself.
- **REQ-03 (Unwanted behavior):** If a claimed metric or catch count changes after this article is drafted (e.g., a 6th verify-before-lock catch occurs, or a spec's revision count increases), then the article shall be revised to reflect the current count — not left silently stale while the rest of the project's trackers move on.

### 5.2 Audience and differentiation

- **REQ-04 (Ubiquitous):** The article shall explicitly address what is different about applying SDD in a security-engineering + compliance context versus generic software development, rather than repeating generic SDD advice already well-covered by sources already reviewed for this project (see `docs/research-notes.md`'s registry).
- **REQ-05 (Ubiquitous):** The article shall be written for a reader familiar with general security/compliance concepts (MITRE ATT&CK, ISO 27001, Secure Score) but not with this project's internal codebase — it shall not assume shared context beyond what is explained inline.

### 5.3 Structure

- **REQ-06 (Ubiquitous):** The article shall include, at minimum, all 7 elements listed in section 4 — omitting the honest-limitations section or the differentiation statement is not acceptable, since both are load-bearing for this article's stated purpose (REQ-02, REQ-04).

### 5.4 Maintenance

- **REQ-07 (Event-driven):** When a new spec is authored or a new verify-before-lock catch occurs after this article's initial publication, the author shall evaluate whether the article should be revised to include it, rather than treating the article as a permanently frozen snapshot.
- **REQ-08 (Optional feature):** Where the article is revised after initial publication, it shall carry its own lightweight revision log (mirroring the discipline every spec in this project already follows), so a reader can tell whether the article reflects the project's current state or an earlier one.

## 6. Non-Functional Requirements

- **NFR-01:** This is a pure documentation task — no Azure dependency, no code, fully producible during the current subscription billing block.
- **NFR-02:** No fixed length requirement, but the article should remain readable in a single sitting (informal target: roughly 1500-2500 words) rather than becoming exhaustive documentation — the spec files themselves already serve that more detailed purpose.

## 7. Task Breakdown

**Why "drafting passes" rather than build batches:** this is a writing deliverable, not code — the batches below reflect drafting/verification passes, not units handed to a coding agent.

| Batch | REQs covered | Description | Depends on | Azure write required? |
|---|---|---|---|---|
| 1 | REQ-01, REQ-06 | Draft the core narrative structure with all 7 required sections, sourcing each catch from the actual spec Revision Logs | - | No |
| 2 | REQ-02, REQ-04, REQ-05 | Write the honest-limitations section, the differentiation framing, and calibrate tone/assumed-context for the target audience | Batch 1 | No |
| 3 | REQ-03, REQ-07, REQ-08 | Establish the article's own lightweight revision-log discipline, so future updates (new catches, new specs) are tracked rather than silently blended in | Batch 1, 2 | No |

**Status of these batches as of this spec's authoring date:** Batches 1 and 2 are effectively done — a full draft already exists (`docs/writing/sdd-security-compliance-case-study.md`), written before this spec was formalized. Batch 3 (the article's own revision-log discipline) has **not** been applied yet — the existing draft has no revision-log footer.

## 8. Acceptance Criteria (checklist)

- [x] Draft article produced, covering all 5 documented verify-before-lock catches with specific technical detail (table names, real numbers) rather than vague generalities (REQ-01, REQ-06)
- [x] Honest-limitations section present, explicitly naming what the methodology has not yet accomplished (REQ-02)
- [x] Differentiation framing present — explicit contrast against generic SDD content (REQ-04)
- [x] Audience calibration present — assumes security/compliance familiarity, not codebase familiarity (REQ-05)
- [ ] **Not yet done:** a dedicated verification pass confirming every specific claim in the drafted article (numbers, table names, dates) exactly matches its cited source — see Open Question 3, this is the most important remaining step
- [ ] **Not yet done:** the article's own revision-log footer (REQ-08) — the current draft has none
- [ ] **Not yet decided:** final publish location (see Open Question 2)

## 9. Open Questions

1. Should the case-study article carry its own lightweight Revision Log, the same way every spec in this project does, so future readers can tell whether it reflects the project's current state? **Recommendation:** yes — add a short "Article Revision Log" footer, applying REQ-07/REQ-08's discipline consistently with how the rest of this project already treats its documentation.
2. Where should the article live — `docs/writing/` inside the repository (for portfolio value visible directly on GitHub) versus an external blog/LinkedIn post kept outside the repo? **Recommendation:** keep a copy in-repo regardless of any external publication, since the repository itself is part of this project's portfolio value chain (per Purpose #3, established earlier this session).
3. **Most important open item:** a verification pass confirming every specific claim in the drafted article (numbers, table/resource names, dates) exactly matches what is recorded in the cited specs' Revision Logs and `docs/backlog-status.md`'s Metrics section has **not yet been run**. Skipping this check here, of all places, would be a direct contradiction of the article's own argument. **Recommendation:** run this verification before treating the article as final — ideally the very next action after this spec is authored.

## 10. Traceability

This spec's content requirements are drawn entirely from artifacts already produced this session: the Revision Logs of specs #1 through #9, `docs/backlog-status.md`'s Metrics section (catch count, spec count), and `docs/research-notes.md`'s registry (used to justify the differentiation claim in REQ-04 — the generic SDD sources already reviewed genuinely don't cover this angle). It is Group C (R&D/Methodology), alongside `security-investment-cost-effectiveness-model.spec.md` and `sdd-methodology-baseline.spec.md` — all three are meta relative to the feature-oriented specs #1-#7, describing the project's own process and its documentation rather than application behavior.

**Note on relationship to `sdd-methodology-baseline.spec.md`:** that spec documents the methodology itself as an internal, checkable process contract (Tier 2 baseline, EARS requirements about how specs should be authored). This spec is different — it specifies requirements for an *external-facing narrative artifact about* that same methodology. They share source material but serve different audiences and should not be merged.

## Revision Log

| Date | Change | Reason |
|---|---|---|
| 28.07.2026 | Initial spec created, formalizing requirements for the case-study article draft already produced earlier the same day | Following a request to formalize this R&D direction the same way `security-investment-cost-effectiveness-model.spec.md` was formalized — as a structured EARS spec, not a freeform document |