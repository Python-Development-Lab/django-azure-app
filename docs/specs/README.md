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
| 1 | [`evidence-linked-attack-mapping.spec.md`](./evidence-linked-attack-mapping.spec.md) | `SEC-DASH-EVIDENCE-01` | Draft | None | docs-only | 2 |
| 2 | [`sentinel-rules-validation-trail.spec.md`](./sentinel-rules-validation-trail.spec.md) | `SEC-DASH-VALIDATION-01` | Draft | None (shares incident data with #1, see below) | docs-only | 1 |
| 3 | [`evidence-chain-plantuml-diagrams.spec.md`](./evidence-chain-plantuml-diagrams.spec.md) | `SEC-DASH-DIAGRAMS-01` | Draft | **#1 and #2** (must be implemented first — see Implementation Order) | docs-only | 1 |
| 4 | [`ioc-reputation-lookup.spec.md`](./ioc-reputation-lookup.spec.md) | `SEC-DASH-IOC-01` | Draft | None | mixed (spec/code writable now; live test against `/security/alerts/` requires Azure) | 3 |
| 5 | [`security-md-honest-limitations.spec.md`](./security-md-honest-limitations.spec.md) | `SEC-DOCS-HONEST-LIMITATIONS-01` | Draft | References facts from #1–#3 and `docs/compliance/azure-platform-certifications.md` (factual consistency only, not a data-model dependency) | docs-only | 1 |

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
```
Spec #5 references facts established in Group A (incident dates, technique IDs) for consistency, but has no code-level or data-model dependency — it can be drafted and refined in parallel with Group A's implementation, as long as incident details are kept in sync.

## Revision Notes (see each file's own Revision Log for full detail)

- **Spec #1** was revised once after direct portal inspection confirmed the exact MITRE ATT&CK technique IDs for the Critical Attack Path, replacing a placeholder.
- **Spec #4** is the most-revised spec in this set (2 revisions after the initial draft) — its first revision incorrectly deprioritized the primary data source after querying a deprecated legacy Azure table; a follow-up check against the correct table reversed that decision. This is the clearest example in the project of the "verify-before-lock" cycle: draft → check assumption against real data → correct the spec accordingly.
- **Specs #2, #3, #5** were each authored complete in a single pass, since the real findings they depend on (the Critical Attack Path, its 4 technique IDs) were already confirmed earlier in the same session — no post-hoc revision was needed.

## Related Documents (not specs, but closely tied to this index)

| Document | Relationship |
|---|---|
| `docs/backlog-status.md` | Broader backlog view (43 items total); tracks which items have a spec here versus which are still unspecified |
| `docs/compliance/azure-platform-certifications.md` | Shared-responsibility reference cited by Spec #5 |
| `docs/security/rule-validation/` (to be created per Spec #2) | Output of implementing Spec #2 |
| `docs/diagrams/evidence-chain-*.puml` (to be created per Spec #3) | Output of implementing Spec #3 |

## Maintenance Note

Update this index whenever:
1. A spec's status changes (Draft → In Progress → Implemented) — update the Status column.
2. A spec is revised — update the Revisions count here and add the detail to that spec's own Revision Log.
3. A new spec is authored — add a new row, and update Implementation Order if it has dependencies on existing specs.
4. A spec is implemented — consider moving its row to an "Implemented" section at the bottom of this table (not yet needed, since none are implemented as of this document's creation) so the active index stays focused on in-flight work.