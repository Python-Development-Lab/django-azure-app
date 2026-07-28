# Spec: Evidence-Chain PlantUML Diagrams

**Status:** Draft
**Feature ID:** SEC-DASH-DIAGRAMS-01
**Related backlog item:** Evidence-Chain PlantUML Diagrams (27.07.2026, Phase 2 upgrade path — scoped down from AdversaryGraph's full "Evidence-to-Detection Graph" concept)
**Owner:** Vitalii Shevchuk
**Target surface:** `docs/diagrams/` (new `.puml` files, using the existing C4-PlantUML toolchain already present in `docs/diagrams/lib/`)

---

## 1. Overview

Produce narrative PlantUML diagrams — one per known real security incident/attack path — visualizing the full evidence-to-decision chain (Evidence → Claim → ATT&CK → Telemetry → Rule → Validation → SIEM Result → Decision) using the project's existing PlantUML/C4 toolchain. This is a documentation-only visualization layer, not a graph database or new schema.

## 2. Problem Statement

Almost every link in this 8-step chain already exists somewhere in the project — the `evidence` array in `attack_data.json` (Evidence-Linked ATT&CK Mapping spec), the per-rule records in `docs/security/rule-validation/` (Sentinel Rules Validation Trail spec), real `SecurityAlert` entries, and documented response decisions — but these facts are scattered across separate files with no single narrative view connecting them for a given incident. A PlantUML diagram per incident provides that narrative view cheaply, without building the full graph-database "Evidence-to-Detection Graph" that a production CTI tool (AdversaryGraph) implements, which is disproportionate to this project's scale (3 known incidents/attack paths).

## 3. Scope

**In scope:**
- One `.puml` diagram per currently-known real incident (3 as of this spec's authoring date — see section 4)
- Diagrams built strictly from facts already recorded in `attack_data.json` and `docs/security/rule-validation/`
- Reuse of the existing C4-PlantUML library and devcontainer tooling (Java 21, Graphviz) already used for the project's 5 existing diagrams

**Out of scope (explicitly deferred):**
- A graph database or Django models representing Evidence/Claim/Rule/Decision as first-class entities (defer to a real Security Dashboard Phase 2 decision, per the 24.07.2026 backlog item on Neo4j Aura vs. d3graph)
- Automatic diagram generation from JSON/markdown sources (manual authorship is proportionate at 3 diagrams; revisit only if the incident count grows substantially)
- A general schema/template system for hypothetical future incidents beyond the naming convention in REQ-06

## 4. Data Model

**Files to produce:**

```
docs/diagrams/
  evidence-chain-nmap-2026-06-26.puml
  evidence-chain-zerotrust-devices.puml
  evidence-chain-critical-attack-path-appservice-keyvault.puml
```

**Per-diagram 8-step structure** (each step is a node/stage in the sequence or activity diagram):

1. **Evidence** — the real, dated observation (e.g., NMap scan, device fingerprint anomaly, Defender Attack Path finding)
2. **Claim** — the behavior this evidence is asserted to represent (e.g., reconnaissance/port-scanning; device impersonation; lateral movement via Managed Identity)
3. **ATT&CK** — the mapped technique(s), matching exactly the `technique_id` values already recorded in `attack_data.json`'s `evidence` array for this incident
4. **Telemetry** — the required data source, matching the "Required telemetry" section of the corresponding rule's validation-trail record where one exists
5. **Rule** — the Sentinel analytics rule (if any) associated with detecting this evidence
6. **Validation** — a direct reference to (not a restatement of) the relevant section of the rule's validation-trail document
7. **SIEM Result** — the real `SecurityAlert`/Defender finding entry
8. **Decision** — the documented response or explicit absence of one (see REQ-07)

## 5. Requirements (EARS notation)

### 5.1 Diagram content and sourcing

- **REQ-01 (Ubiquitous):** The system (documentation set) shall provide one `.puml` diagram per currently-known real incident, each following the 8-step structure in section 4.
- **REQ-02 (Ubiquitous):** Each diagram's content shall be derived only from facts already recorded in `attack_data.json`'s `evidence` array or the corresponding file(s) in `docs/security/rule-validation/` — no step shall introduce a fact not already documented in one of those two sources.
- **REQ-03 (Unwanted behavior):** If a diagram step has no corresponding documented fact in either source, then that step shall be rendered with an explicit "not yet documented" label rather than left blank or filled with an invented/assumed value.
- **REQ-04 (Ubiquitous):** Diagrams shall follow the project's existing PlantUML conventions — ASCII-only characters (no em-dashes or other Unicode punctuation), referencing the existing C4-PlantUML library in `docs/diagrams/lib/` where applicable, for GitHub Actions rendering compatibility.

### 5.2 Cross-document consistency

- **REQ-05 (Ubiquitous):** Incident dates, technique IDs, and rule names used in each diagram shall exactly match the corresponding entries in `attack_data.json` and `docs/security/rule-validation/*.md` — any discrepancy between a diagram and either source document is a defect, not an acceptable variation.
- **REQ-06 (Event-driven):** When a new real incident or attack path is discovered in the future, a new diagram file shall be added following the same naming convention and 8-step structure, rather than retrofitting or overloading an existing diagram with an unrelated incident.

### 5.3 Honest representation of open gaps

- **REQ-07 (State-driven):** While a diagram's "Decision" step corresponds to an incident where no automated response/playbook exists (per the 24.07.2026 Automated Response Gap backlog item), the diagram shall render that terminal node with a visually distinct marker (e.g., dashed border, explicit "no automated response" label) rather than as a closed, fully-resolved endpoint.

## 6. Non-Functional Requirements

- **NFR-01:** No new tooling is required — the devcontainer already includes Java 21, Graphviz, and the C4-PlantUML libraries used for the project's existing 5 diagrams.
- **NFR-02:** This is a pure documentation task with no dependency on Azure write access — all three diagrams can be authored and committed while the subscription billing issue is unresolved.
- **NFR-03:** Scope is strictly limited to the 3 currently-known incidents; do not pre-build diagrams or placeholders for hypothetical future incidents.

## 7. Acceptance Criteria (checklist)

- [ ] `evidence-chain-nmap-2026-06-26.puml` created, renders without errors, all 8 steps populated from documented facts
- [ ] `evidence-chain-zerotrust-devices.puml` created, renders without errors, all 8 steps populated from documented facts
- [ ] `evidence-chain-critical-attack-path-appservice-keyvault.puml` created, renders without errors, ATT&CK step includes all 4 confirmed technique IDs (T1552, T1555.005, T1021, T1021.007) from this session's Attack Path finding
- [ ] Every incident date, technique ID, and rule name in all three diagrams matches exactly against `attack_data.json` and the corresponding `docs/security/rule-validation/*.md` file
- [ ] Any diagram whose "Decision" step reflects the absence of an automated response renders that node with a visually distinct "incomplete" marker
- [ ] All three files use ASCII-only characters and follow existing project PlantUML conventions

## 8. Open Questions

1. Whether the Critical Attack Path diagram should render its 4 confirmed technique IDs (T1552, T1555.005, T1021, T1021.007) as one combined ATT&CK step or four separate parallel steps. Recommendation: one combined step listing all 4, since they represent a single continuous exploitation chain discovered as one Defender Attack Path finding, not four independent incidents — matching how `attack_data.json` already groups them under one `attack_path_id`.
2. Whether rendered PNG/SVG output should be committed alongside the `.puml` source files, or whether only source is committed and rendering happens in CI (matching whatever convention the existing 5 diagrams already follow). Recommendation: inspect the existing `docs/diagrams/` directory structure before authoring these three, and match whatever convention is already in place rather than introducing a second convention.

## 9. Traceability

This spec depends on both the Evidence-Linked ATT&CK Mapping spec (`docs/specs/evidence-linked-attack-mapping.spec.md`) and the Sentinel Rules Validation Trail spec (`docs/specs/sentinel-rules-validation-trail.spec.md`) as its sole sources of truth (per REQ-02) — this spec should be implemented last among the three, after both source documents exist, to avoid diagrams drifting from not-yet-finalized evidence/validation content. If a future Security Dashboard Phase 2 (graph database) is pursued, the 8 step-types defined here become the starting schema for graph nodes/edges, per the original 27.07.2026 backlog item's stated upgrade path.