# Project Constitution — django-azure-app

**Purpose:** A short, persistent reference of this project's non-negotiable rules — architectural, security, and process. Every spec, every piece of implementation, and every AI coding agent working on this project should be checked against this file. Unlike a spec, this file is not about *what* to build next — it's about *what must always remain true*, regardless of which feature is being worked on.

**Inspired by:** GitHub Spec Kit's `constitution.md` concept (reviewed 28.07.2026) — adopted as a standalone practice for this project rather than the full Spec Kit toolchain, per the decision recorded in `docs/research-notes.md`.

**Every rule below is grounded in a real incident, decision, or finding from this project's history — not invented for completeness.** If you want to challenge or change a rule, find the source incident first and understand why it exists before removing it.

---

## 1. Azure Identity & Secrets

- **MUST** use `ManagedIdentityCredential()` without a `client_id` argument for System-Assigned Managed Identity. The `client_id` argument is for User-Assigned MSI only — mixing these up has been a real source of confusion in this project.
- **NEVER** hardcode a secret, connection string, or API key inline in code, scripts, or CI workflow files. All secrets live in Azure Key Vault, retrieved via MSI.
- **MUST** use `--output none` with `az webapp config appsettings set` and any similar command that could print secrets to stdout/CI logs. Omitting this printed `DB_PASSWORD`, `SECRET_KEY`, and `EXTERNAL_ID_CLIENT_SECRET` in plaintext earlier in this project's history — these are still pending rotation as of this writing.
- **MUST** use the `BUILDING=true` environment variable pattern to handle Key Vault being unavailable during the Oryx build phase.

## 2. Terraform & Infrastructure Changes

- **NEVER** allow an AI-generated suggestion (e.g., from the planned "Ask AI About This Alert" panel) to automatically run `terraform apply` or any other infrastructure-modifying command. Suggested fixes are text for human review only — this is a hard, permanent boundary, not a placeholder to relax later (see `ask-ai-alert-panel.spec.md` REQ-10).
- **MUST** verify that any Terraform resource name mentioned in an AI-generated suggestion actually exists in the current Terraform state before treating the suggestion as reliable (see `ask-ai-alert-panel.spec.md` REQ-05).
- **MUST NOT** commit `terraform.tfvars` — it is gitignored and not persisted between Codespace sessions by design; recreate it each session.
- **MUST** scope role assignments (e.g., for `django-azure-sp`) to the resource group, not the subscription, going forward. Subscription-scope `Contributor` + `User Access Administrator` on the CI service principal is a confirmed, documented over-privilege finding (25.07.2026, corroborated by CSPM export 27.07.2026) — new grants must not repeat this pattern without an explicit, documented justification in a spec's NFR section.
- **MUST** ensure GitHub Secret `TERRAFORM_OBJECT_ID` holds the CI service principal's object ID, not a personal object ID. Mixing these up caused a real incident (20.07.2026).

## 3. Security Claims & Documentation Integrity

- **MUST NOT** mark an ATT&CK technique, a compliance control, or any other security claim as `mitigated` or `detected` unless the underlying control genuinely exists as working code — not as aspirational description. `RiskScoringMiddleware`/KBSSE Threat Ontology was found (25.07.2026) to exist only as descriptive text in `attack_data.json`, not as real middleware, despite techniques being marked `detected` on that basis. Do not repeat this pattern.
- **MUST** verify any factual claim about live code, data, or infrastructure directly before asserting it in a spec or documentation — never from memory or inference alone. This project has caught 5 real violations of this rule already (see `docs/backlog-status.md`'s Metrics section); each one would have gone unnoticed without direct verification.
- **MUST NOT** publish specific exploit-enabling details (exact CVE numbers, exact vulnerable package versions, exact attack chains) in a public-facing document (`SECURITY.md`) for a vulnerability that is not yet remediated. Describe the gap category and remediation status only, until the fix ships (see `security-md-honest-limitations.spec.md` Open Question 2).

## 4. Compliance Document Format

- **MUST** follow the exact frontmatter format (`control_id`, `regulation`, `title`, `status`, `date` between `---` markers) plus `## Description` / `## Evidence` / `## Gaps` sections for any file placed directly in `docs/compliance/*.md` — the live `_parse_compliance_file()` parser depends on this exact structure and will silently misparse anything that doesn't follow it.
- **MUST NOT** place a non-control-record document (e.g., a shared-responsibility reference, a general compliance note) directly in `docs/compliance/` — use a subdirectory like `docs/compliance/reference/` instead. A file placed incorrectly here already risked silently corrupting the live `security_compliance` dashboard panel's control count (caught and fixed 28.07.2026).

## 5. Spec-Driven Development Process

- **MUST** run the Triage checklist (top of `docs/specs/TEMPLATE.md`) before deciding to write a new spec — not everything needs one, and not everything should skip one. See that file for the decision criteria.
- **MUST** write every spec following the 10-section structure in `docs/specs/TEMPLATE.md`, using EARS notation (Ubiquitous / Event-driven / State-driven / Unwanted behavior / Optional feature) for every requirement, numbered sequentially.
- **MUST** verify every factual claim in a spec's Problem Statement, Data Model, or Requirements against the live system before treating the spec as ready for implementation (this is rule #3's process-level counterpart).
- **MUST** record any post-authoring correction in the spec's own Revision Log — never silently edit Requirements or Acceptance Criteria without a trace.
- **MUST** batch a spec's requirements into a Task Breakdown table (roughly 3-6 requirements per batch) before handing it to an AI coding agent, to mitigate context-rot risk — unless the spec has fewer than ~6 requirements total, in which case a single batch is fine.
- **MUST** run an "Explore" step (read the actual relevant files, confirm real schemas/conventions) before implementing any spec's requirements — do not implement directly against a spec's assumptions without confirming them against the live codebase first. This is the methodology's identified biggest remaining gap; treat it as a hard MUST going forward, not an optional nice-to-have.
- **MUST** populate a spec's Requirement Traceability Verification table — ideally in a fresh agent session, separate from the one that wrote the implementation — before changing that spec's Status from `Draft` to `Implemented`.
- **MUST** keep the three tracking artifacts current whenever a spec is authored, revised, or a new external source is researched: `docs/backlog-status.md`, `docs/specs/README.md`, `docs/research-notes.md`.

## 6. Scope Discipline

- **MUST NOT** introduce new Azure infrastructure, new external dependencies, or new architectural complexity (e.g., a graph database, a multi-agent orchestration system) unless a spec's Non-Functional Requirements explicitly justify it against this project's actual scale. This project has repeatedly and deliberately rejected over-engineered patterns found in comparable frameworks (58-agent orchestration, SQLite-backed knowledge graphs, full CTI-workbench functionality) as disproportionate to a solo, ~10-spec-scale project — new proposals should be held to the same standard.
- **MUST NOT** retroactively write a full baseline spec for genuinely trivial, already-built work — the retroactive-baseline pattern (see `docs/specs/README.md`'s Baseline Specs section) is for subsystems worth formally documenting, not everything that has ever been built.

## 7. Communication Convention

- **MUST** produce technical output (code, specs, documentation, commit messages) in English.
- **MAY** use Ukrainian for explanations, discussion, and session communication, per this project owner's established working style.

---

## Maintenance Note

Add a new rule here only when it is grounded in a real incident, decision, or finding — not as a hypothetical "good practice." If a rule listed here is ever deliberately violated for a documented, justified reason, record that exception in the relevant spec's NFR or Open Questions section, referencing this file — do not silently ignore a constitutional rule without a trace, for the same reason specs require a Revision Log rather than silent edits.