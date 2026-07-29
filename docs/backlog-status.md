# Backlog Status — django-azure-app

**Last updated:** 28.07.2026 (revised same day — see "Newly Discovered Pre-Existing Artifacts" section below)
**Purpose:** Single consolidated view of all outstanding backlog items, tracking (1) whether a formal spec exists in `docs/specs/`, and (2) whether implementation is blocked pending Azure subscription write-access restoration versus available now (docs/config-only).

**Status legend:**
- **Spec:** `has spec` | `no spec`
- **Blocker:** `blocked-on-azure` (requires Azure write access — Terraform apply, `az` write commands, live resource changes) | `docs-only` (can be authored/implemented without Azure write access) | `mixed` (spec/docs work possible now, but full implementation/testing requires Azure)

---

## 1. Critical / Time-Sensitive

| Item | Spec | Blocker | Priority | Source |
|---|---|---|---|---|
| Rotate 3 exposed secrets (`DB_PASSWORD`, `SECRET_KEY`, `EXTERNAL_ID_CLIENT_SECRET`) | no spec | blocked-on-azure | CRITICAL | Long-standing; reinforced by 27.07.2026 Attack Path finding |
| Update GitHub Secret `AZURE_CLIENT_SECRET` to match rotated Entra app secret | no spec | blocked-on-azure | CRITICAL | Long-standing (AADSTS7000215 recurrence risk) |
| Update outdated `cryptography` package (closes Critical Attack Path entry point) | no spec | blocked-on-azure | CRITICAL | 27.07.2026 — confirmed root cause of Critical Defender Attack Path `c81dcadc-7b9c-3066-79cc-74be12d8b64f` |
| Fix Terraform state lock / `Terraform Apply` CI failure | no spec | blocked-on-azure | CRITICAL | 28.07.2026 — pipeline failing, likely tied to billing read-only period |
| Resolve Azure subscription billing (`Auto pay failed`, invoice G169932806, $174.84) | n/a (account admin, not a project spec) | blocked-on-azure (is itself the blocker) | CRITICAL | 27–28.07.2026 |

## 2. RBAC / IAM

| Item | Spec | Blocker | Priority | Source |
|---|---|---|---|---|
| Wire `human_admin_object_id` into pipeline (GitHub Secrets: `TERRAFORM_OBJECT_ID`, `HUMAN_ADMIN_OBJECT_ID`) | no spec | blocked-on-azure | High | 20.07.2026 code committed, not yet wired |
| Scope down `django-azure-sp` role assignments (subscription → resource-group scope) | no spec | blocked-on-azure | High | 25.07.2026 finding, corroborated 27.07.2026 by CSPM export |
| Evaluate ABAC conditions narrowing `User Access Administrator` grants | no spec | blocked-on-azure | Medium | 25.07.2026 |
| Managed Identity as Federated Identity Credential (cross-tenant Graph API access) | no spec | blocked-on-azure | Low (not yet needed) | 24.07.2026, extends OIDC migration scope |
| Verify Legacy Authentication blocked for CIAM tenant | no spec | mixed (check may be read-only; fix may need config change) | Medium | 24.07.2026, CyberDefenders AzureSpray comparison |
| PIM for human admin (`147bf926-...`) Owner-at-subscription-scope | no spec | blocked-on-azure | Medium | 25.07.2026 / 27.07.2026 CSPM confirmation |

## 3. CI/CD OIDC Migration

| Item | Spec | Blocker | Priority | Source |
|---|---|---|---|---|
| Migrate GitHub Actions from `AZURE_CREDENTIALS` (client secret) to OIDC/Federated Identity | no spec | blocked-on-azure | High | 21.07.2026 |
| — sub-item: workspace-to-role mapping config | no spec | docs-only (design), blocked-on-azure (implement) | — | 25.07.2026, Pinterest article comparison |
| — sub-item: separate apply-authorization step (Environment protection rules) | no spec | docs-only (design), blocked-on-azure (implement) | — | 25.07.2026 |
| — sub-item: Terraform backend validation against workspace | no spec | docs-only (design), blocked-on-azure (implement) | — | 25.07.2026 |

## 4. Security Dashboard / Phase 2

| Item | Spec | Blocker | Priority | Source |
|---|---|---|---|---|
| Evidence-Linked ATT&CK Mapping | **has spec** (`evidence-linked-attack-mapping.spec.md`) | docs-only | High | 27.07.2026, confirmed with real Attack Path data |
| Sentinel Rules Validation Trail | **has spec** (`sentinel-rules-validation-trail.spec.md`) | docs-only | High | 27.07.2026 |
| Evidence-Chain PlantUML Diagrams | **has spec** (`evidence-chain-plantuml-diagrams.spec.md`) | docs-only | Medium | 27.07.2026 |
| IOC Reputation Lookup for Defender alerts | **has spec** (`ioc-reputation-lookup.spec.md`) | mixed (spec/code writable now; live test needs Azure) | Medium | 27.07.2026, confirmed MDTI data active |
| Defender plans status badge on Security Dashboard | no spec | mixed | Medium | 27.07.2026, `Arm` plan gap identified |
| Secure Score + Sentinel incidents/rules-health metrics panel | no spec | mixed | Medium | 27.07.2026 |
| Security Dashboard Phase 2 (d3graph vs Neo4j Aura, betweenness centrality on gap techniques) | no spec | docs-only (design decision), blocked-on-azure (Neo4j Aura provisioning if chosen) | Medium | 24.07.2026 |
| "Ask AI about this alert" panel (Claude API + citation/verification safeguards) | no spec (**full STRIDE threat model already exists**: `docs/threat-models/0001-ask-ai-alert-panel.md` + `.en.md`, dated 25.07.2026, discovered 28.07.2026) | mixed | Medium | 21.07.2026, refined 24.07.2026, threat-modeled 25.07.2026 |
| ADR panel on Security Dashboard UI | no spec (the ADR files themselves already exist and are committed: `docs/adr/0001-nsg-flow-logs-rejected.md`, `docs/adr/0002-nat-gateway-deferred.md` — only the dashboard *UI panel* for surfacing them is undecided) | docs-only | Low (deferred) | 24.07.2026 |
| Static C4 infrastructure diagram on Security Dashboard | no spec | docs-only | Low | 28.07.2026 |
| "Open Attack Path Analysis in Azure Portal" deep-link button | no spec | docs-only (config) | Low | 28.07.2026 |

## 5. Sentinel / Detection

| Item | Spec | Blocker | Priority | Source |
|---|---|---|---|---|
| Distributed password-spray detection rule (`FailCount>30 AND UniqueIPs>5` over 15m) | no spec | blocked-on-azure | High | 24.07.2026, CyberDefenders AzureSpray comparison |
| Automated response playbook (Logic App → `revokeSignInSessions`) | no spec (**real playbook already drafted**: `docs/playbooks/T1110-http-brute-force.md`, dated 25.07.2026, discovered 28.07.2026 — its own Eradication section explicitly notes `revokeSignInSessions` automation "not yet implemented, see backlog", confirming this item is still genuinely open) | blocked-on-azure | Medium | 24.07.2026, playbook drafted 25.07.2026 |
| Reuse CIAM SigninLogs KQL patterns (ResultType 50126/50053/0) | no spec | blocked-on-azure (pending Event Hub + Function App bridge) | Low (dependency not ready) | 24.07.2026 |
| Custom banned-password policy for CIAM (reference: NIST guidance, 1000-term cap) | no spec | blocked-on-azure | Low | 24.07.2026 |

## 6. Networking / Infrastructure

| Item | Spec | Blocker | Priority | Source |
|---|---|---|---|---|
| WAF/IP restrictions via Application Gateway v2 (closes T1595 gap) | no spec | blocked-on-azure | **Highest** (per project's own stated priority) | Long-standing; candidate confirmed 24.07.2026 over Front Door |
| NAT Gateway (conditional — revisit only if Neo4j Aura/external IP-allowlisted service is added) | no spec | blocked-on-azure (if pursued) | Low (deferred) | 24.07.2026 |
| Governance Terraform module | no spec | blocked-on-azure | Medium | Long-standing |

## 7. Data / Operational

| Item | Spec | Blocker | Priority | Source |
|---|---|---|---|---|
| PostgreSQL least-privilege role migration (`django_app_user`, DML-only) | no spec | blocked-on-azure | High | 24.07.2026 real finding (app connects as `azuresu`) |
| Formalize `kv-to-sentinel` / `pg-to-sentinel` diagnostic settings in Terraform | no spec | blocked-on-azure | Medium | 24.07.2026 (currently manual `az rest` artifacts) |
| Verify and set `https_only = true` on App Service | no spec | blocked-on-azure | Medium | 21.07.2026 |
| ThreadPoolExecutor parallelization for Log Analytics queries | no spec | blocked-on-azure | Low | 21.07.2026 (only relevant if consolidated Security endpoint is built) |

## 8. Compliance

| Item | Spec | Blocker | Priority | Source |
|---|---|---|---|---|
| SECURITY.md (CRA Annex I VDP) + Honest Limitations section | **has spec** (`security-md-honest-limitations.spec.md`) | docs-only | High | 21.07.2026, refined 28.07.2026 |
| `docs/compliance/mcsb-cross-reference.md` (map 16 failed MCSB controls to ISO 27001 A.8.x records) | no spec (**significantly re-scoped 28.07.2026**: a live, working compliance-parsing system already exists — 34 real ISO 27001 A.8.x control files in `docs/compliance/*.md`, each with `control_id`/`regulation`/`status` frontmatter + `## Description`/`## Evidence`/`## Gaps` sections, rendered live at `/security/compliance/` via `_get_compliance_mappings()`. This item is no longer "create a new cross-reference document" — it is "add MCSB-mapping fields to the existing, already-rendered control records") | docs-only | Medium | 25.07.2026; infrastructure discovered 28.07.2026 |
| Re-run failed MCSB controls query (check if logging-related items improved post 24.07.2026 diagnostic-settings fix) | no spec | mixed (read-only check, but needs stable Azure access) | Medium | 25.07.2026 |
| Investigate DP.3 (encrypt in transit) via Portal UI — API returned empty assessment data | no spec | mixed | Low | 25.07.2026 |
| Verify Defender CloudPosture extension costs (AgentlessVmScanning etc.) aren't adding meaningful cost | no spec | mixed (portal check) | Low | 21.07.2026 |

## 9. Other

| Item | Spec | Blocker | Priority | Source |
|---|---|---|---|---|
| Lenovo Threat Modeler interview preparation (English B2, STAR/SAR framework) | n/a (not a project spec — career/interview prep) | docs-only | Medium | Long-standing |

---

## Newly Discovered Pre-Existing Artifacts (Verification Pass, 28.07.2026)

While running the Security Dashboard baseline spec's Verification Batches, direct inspection of the live codebase and filesystem surfaced substantial prior work not previously reflected in this document or in `docs/specs/`. This session had been treating several backlog items as "no spec, not started" when real, dated artifacts already existed. Recorded here so this gap doesn't recur.

| Artifact | What it is | Relevance |
|---|---|---|
| `docs/threat-models/TEMPLATE.md` + `.en.md` | STRIDE threat-model template, explicitly annotated as aligned with Spec-Driven Development ("узгоджено з принципом Spec-Driven Development") | Confirms SDD-style thinking predates this session's formal adoption — at least for threat modeling |
| `docs/threat-models/0001-ask-ai-alert-panel.md` + `.en.md` (25.07.2026) | Complete STRIDE analysis for the "Ask AI about this alert" panel, with concrete action items (rate limiting, audit logging, read-only MSI, citation requirements, Terraform-state verification before showing suggestions) | See row 4 update above — this is most of the design work an EARS spec for this feature would need |
| `docs/playbooks/PLAYBOOK-TEMPLATE.md` + `docs/playbooks/T1110-http-brute-force.md` (25.07.2026) | Real incident-response playbook (SANS+NIST hybrid structure, adapted from austinsonger/Incident-Playbook), covering the HTTP brute-force Sentinel rule | See row in section 5 above; also empirically confirms cloud-range IPs rarely appear in MDTI feeds (24.07.2026 finding) — directly relevant to `ioc-reputation-lookup.spec.md`'s `known_azure_range` classification design |
| `docs/adr/0001-nsg-flow-logs-rejected.md`, `docs/adr/0002-nat-gateway-deferred.md` | Two Architecture Decision Records, already committed | Confirms the ADR-authoring backlog item (24.07.2026) was completed; only the dashboard UI panel for surfacing them remains undecided |
| `docs/compliance/*.md` (34 files) + `_get_compliance_mappings()`/`_parse_compliance_file()` in `core/views.py`, rendered live at `/security/compliance/` | Full ISO 27001:2022 Annex A control-mapping system (A.8.1 through A.8.34), each file with `control_id`/`regulation`/`title`/`status`/`date` frontmatter | Substantially re-scopes the MCSB cross-reference backlog item (see row update above) |
| `create_threat_models_bilingual.sh`, `fix_attack_data_claims.sh`, `generate_playbooks.sh`, `integrate_compliance_ui.sh` | Four idempotent "safe insertion" shell scripts from a prior session, left untracked until accidentally committed in `8c08f00` (28.07.2026) | `fix_attack_data_claims.sh` is confirmed to be the source of the already-honest `gap` status on `T1068`/`T1110.004`/`T1528` in the live `attack_data.json` — it did **not** touch `T1567`, corroborating this session's suspicion that `T1567` may still be misclassified as `detected` (see `evidence-linked-attack-mapping.spec.md`'s Additional Findings section) |
| `docs/compliance/azure-platform-certifications.md` (this session's own file) | Was silently at risk of corrupting `security_compliance`'s control count — it contains `---` sequences that would have been misparsed as malformed frontmatter by `_parse_compliance_file()` | Fixed 28.07.2026 by moving to `docs/compliance/reference/`, outside the non-recursive `docs/compliance/*.md` glob |

**Process lesson:** this reinforces, for the third time this session (after `ThreatIntelIndicators` and the `attack_data.json` schema), that this project's own prior-session artifacts are as important a "verify before lock" target as external Azure data. Before writing a new spec for any backlog item, check `find . -iname "*<topic>*"` and `git log --all --oneline -- '*<topic>*'` for prior work, not just this document's own "no spec" label.

---

| Category | Total items | Has spec | No spec | Blocked-on-azure | Docs-only | Mixed |
|---|---|---|---|---|---|---|
| Critical / Time-Sensitive | 5 | 0 | 5 | 5 | 0 | 0 |
| RBAC / IAM | 6 | 0 | 6 | 5 | 0 | 1 |
| CI/CD OIDC Migration | 4 | 0 | 4 | 1 | 0 | 3 (mixed: design now, implement later) |
| Security Dashboard / Phase 2 | 11 | 4 | 7 | 0 | 6 | 5 |
| Sentinel / Detection | 4 | 0 | 4 | 4 | 0 | 0 |
| Networking / Infrastructure | 3 | 0 | 3 | 3 | 0 | 0 |
| Data / Operational | 4 | 0 | 4 | 4 | 0 | 0 |
| Compliance | 5 | 1 | 4 | 0 | 2 | 2 |
| Other | 1 | 0 | 1 | 0 | 1 | 0 |
| **Total** | **43** | **5** | **38** | **22** | **9** | **11** |

**Spec coverage: 5 of 43 items (~12%) have a formal spec.**
**Immediately actionable without Azure (docs-only + design-portion of mixed items): roughly 20 of 43 items** — a substantial amount of work remains available while the Azure subscription billing issue is unresolved.

---

## Recommended Next Specs (docs-only, highest priority first)

1. **WAF/IP restrictions design decision** — the project's own stated *highest priority* item; even though implementation is blocked-on-azure, the Application Gateway v2 vs. Front Door decision (already made 24.07.2026) can be formalized into a spec now, ready to implement the moment Azure access returns.
2. **PostgreSQL least-privilege role migration** — a real, confirmed finding (app running as `azuresu`) with a fully-formed remediation plan already drafted (24.07.2026 session) — ready to become a spec.
3. **"Ask AI about this alert" panel — formalize existing threat model into an EARS spec** (re-prioritized 28.07.2026): the STRIDE analysis is already complete (`docs/threat-models/0001-ask-ai-alert-panel.md`); this is now the cheapest spec to write in the entire backlog, since it's a translation exercise (STRIDE findings → REQ/NFR) rather than new analysis.
4. **`docs/compliance/mcsb-cross-reference.md`** — re-scoped 28.07.2026 to build directly on the discovered live compliance-parsing system rather than starting fresh; directly extends the just-completed Honest Limitations spec.
5. **OIDC migration (with the 3 Pinterest-inspired sub-items)** — the design/architecture portions (workspace-to-role mapping, apply-authorization gating, backend validation) can be fully specified now even though rollout requires Azure.

## Maintenance Note

This document should be updated whenever a new spec is authored (move item from "no spec" to "has spec") or when the Azure subscription billing issue is resolved (re-evaluate which "blocked-on-azure" items become immediately actionable).