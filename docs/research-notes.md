# Research Notes

**Purpose:** A dated, reusable registry of every external article/source reviewed during this project's Spec-Driven Development adoption, so future sessions don't need to re-search the same ground. This is this project's lightweight equivalent of the "research-cache.md" file found in several memory-bank-style SDD frameworks (AI-RPI, Memory Bank pattern) — deliberately kept as a flat markdown log, not a database, consistent with this project's scale.

**Last updated:** 28.07.2026

**How to use this file:** before researching a topic already listed here, check this table first. When you do research something new, add a row — date, source, one-line takeaway, and what it produced (a spec, a backlog item, a template change, or "narrative/context only, no artifact").

---

## Index

| Date reviewed | Source | Core takeaway | Produced |
|---|---|---|---|
| 27.07.2026 | AdversaryGraph v6.0.0 (Andrey Pautov, Medium, 23.07.2026) | CTI-to-detection product; "Evidence-to-Detection Graph" concept (evidence→claims→ATT&CK→telemetry→rules→validation→SIEM→decision) | Backlog items: Evidence-Linked ATT&CK Mapping, IOC Reputation Lookup, Sentinel Rules Validation Trail, Evidence-Chain PlantUML Diagrams (all later became specs #1, #4, #2, #3) |
| 27.07.2026 | AdversaryGraph v5.0 (same author, June 2026) | Predecessor release; "Attack Simulation" feature, same Evidence-to-Detection Graph concept in earlier form | Reinforced the same 4 backlog items above; no new content |
| 27.07.2026 | ThreatMapper Web (1200km.com/threat-matrix, same author) | Public, feature-limited companion tool to AdversaryGraph | No spec produced; noted a naming collision with the unrelated, better-known Deepfence ThreatMapper project, and a commercial-use licensing restriction on the author's tools |
| — (general search, not one article) | Spec-Driven Development overview (IBM, AWS Kiro docs, dev.to field guide, arXiv Piskala paper) | EARS notation, 3-tier maturity model (Spec-First/Spec-Anchored/Spec-as-Source), general SDD rationale | Directly led to adopting SDD methodology for this project (`docs/specs/TEMPLATE.md`, EARS notation choice) |
| 28.07.2026 | "Spec-Driven Development for Product Managers" (Product Managers Club, Medium, 01.06.2026) | "The bottleneck didn't move, it shapeshifted" — from code-writing speed to spec quality | Narrative/communication framing only — no spec or backlog change; useful for explaining the SDD shift to non-technical audiences |
| 28.07.2026 | "My Workflow with Claude: SDD with AgentSpec" (Lorenzo Uriel, Medium, 17.06.2026) | AgentSpec's 5-phase workflow (Brainstorm→Define→Design→Build→Ship→Iterate) with numeric quality gates; KB-first cognitive framework | Directly motivated adding the **Revision Log** section to the spec template (mirrors AgentSpec's `/iterate` cascade-tracking) |
| 28.07.2026 | "The Evolution of Spec-Driven Development" (Enrico Papalini, Medium, 16.05.2026) | Context rot (performance degrades well below context-window limits); "Lost in the Middle" positional bias; 3-tier maturity model in depth; 6 foundational spec elements; Adversarial Agent Pattern (Coordinator/Implementor/Verifier); survey of 11 frameworks | Directly motivated adding the **Task Breakdown** section to the spec template (context-rot mitigation via batching) |
| 28.07.2026 | "Next Trends in the Evolution of Spec-Driven Development" (Enrico Papalini, Medium, 07.06.2026) | 5 macro-trends: Structured-Data-as-Source-of-Truth, Pre-Spec Intake/Intent Kernel, Mission Control/Subagent Delegation, Sealed File-Contracts (frontend-specific, not relevant here), Package/Dependency Hygiene | Reinforced the Task Breakdown design; flagged the still-unresolved Dependabot warning as directly relevant to Trend 5 |
| 28.07.2026 | "Loop Engineering vs. Harness Engineering" (Divy Yadav, Towards AI, 05.07.2026) | Harness engineering (guardrails/permissions/verification) vs. loop engineering (scheduling/stopping/state) as two distinct disciplines; confusing them causes specific, diagnosable failure modes | Categorized `.claude/agents/security-reviewer.md` as a harness artifact; informed REQ-09/REQ-10 framing (permanent guardrails, not one-time checks) in `ask-ai-alert-panel.spec.md` |
| 28.07.2026 | "From Prompt to Production" (Mouez Yazidi, Towards AI, 14.07.2026) | Full 8-stage workflow: Explore→Specify→Clarify→Plan→Tasks→Implement→Verify→Independent Review; concrete example of a spec.md/plan.md/tasks.md structure; independent-review subagent pattern with restricted tools | Directly motivated: **Requirement Traceability Verification** section in the spec template; `.claude/agents/security-reviewer.md`; the still-informal recommendation to run an "Explore" step before implementing any spec (identified as this methodology's biggest remaining gap) |
| 28.07.2026 | "Security Engineering is Dead. It's Time to Adopt Platform Security" (Andrew Blooman, Medium, 11.08.2024) | Proposes splitting "Security Engineer" into Security Operations / DevSecOps / Platform Security roles | Career-framing insight only — no spec; useful for interview/portfolio self-positioning, not project architecture |
| 28.07.2026 | GitHub Spec Kit (official repo, 111k+ stars; FWDays video review of an earlier version) | Official GitHub/Microsoft SDD toolkit — 7-phase workflow (constitution, specify, clarify, plan, tasks, analyze, implement), `constitution.md` as a persistent non-negotiable-rules file the agent checks against continuously, explicit "clarify" phase distinct from "specify," 30+ agent integrations including Claude Code | **Decision: selective adoption, not full toolchain switch.** Full migration rejected as disproportionate to this project's solo scale and as competing with actual remediation priorities (WAF, secrets rotation, RBAC) at a time when sustainable pace matters more than tooling. Adopted the `constitution.md` concept standalone → `docs/specs/CONSTITUTION.md`. The "clarify as a separate phase" and "analyze before implement" ideas were noted as good future candidates but not yet implemented — see `docs/specs/TEMPLATE.md`'s existing gaps list. |
| 28.07.2026 | FWDays video (Ukrainian, "freestyle vibe-coding" vs. Spec-Driven Development, live Spec Kit demo) | Live walkthrough of Spec Kit's specify→plan→tasks→implement flow; articulates 3 core vibe-coding failure modes: (1) curse of knowledge — unstated assumptions the AI fills in on its own; (2) no formal definition of done; (3) lost decision context — the reasoning behind a choice lives only in chat history, not in the project | Motivated academic-sourcing follow-up (next row) and the pre-spec Triage checklist added to `docs/specs/TEMPLATE.md` |
| 28.07.2026 | Academic backing for the FWDays video's 3 core claims (search-verified, not just intuited) | **(1) Curse of Knowledge:** Camerer, C., Loewenstein, G., & Weber, M. (1989). "The Curse of Knowledge in Economic Settings: An Experimental Analysis." *Journal of Political Economy*, 97(5), 1232-1254 — the original paper, building on Fischhoff's 1975 hindsight-bias work; Elizabeth Newton's 1990 Stanford "tapping" experiment is the canonical illustration (tappers predicted ~50% correct guesses, listeners actually got ~2.5%); a 2026 paper ("Emergence: Overcoming Privileged Information Bias in Asymmetric Embodied Agents via Active Querying") directly reframes this bias as a named failure mode in human-AI-agent collaboration specifically. **(2) No definition of done / requirement ambiguity:** an academic study directly measuring the effect — arXiv, "Assessing the Impact of Requirement Ambiguity on LLM-based Function-Level Code Generation" — empirically studies how ambiguous requirements degrade LLM-generated code, the exact mechanism the video describes informally. **(3) Lost decision context:** the established software-engineering term "architectural knowledge vaporization" (tacit architectural rationale lost when documentation is skipped or inadequate) — traced through multiple papers (a pattern-driven documentation approach, an agile-global-software-development study, a CHASE 2013 interview study) and a 2026 paper explicitly proposing ADRs plus LLM-assistants as a mitigation strategy. | Confirms that this project's 3 core methodology components each address a separately, academically-documented failure mode rather than a stylistic preference: the Explore-step MUST in `docs/specs/CONSTITUTION.md` (curse of knowledge), EARS notation + Task Breakdown (requirement ambiguity), and the Revision Log + 3 persistent trackers (architectural knowledge vaporization) |

## Cross-cutting observation

Independent convergence: this project's own `docs/backlog-status.md` + `docs/specs/README.md` + per-file Revision Log pattern was built organically, before any of the above articles were reviewed for this specific purpose — and turned out to closely match the "Memory Bank" pattern documented across at least 4 independent sources found during this research (AI-RPI's `decisions.md`/`lessons.md`/`session-state.md`, the general "Memory Bank" pattern via `CLAUDE.md`/`design.md`, Beads' living-memory JSONL+SQLite store, and Augment Code's `AGENTS.md`). This convergence is treated as a positive signal, not a coincidence — per Papalini's own observation that independently-arrived-at shared design choices are usually correct ones.

## Maintenance Note

Add a new row whenever a new external article/source is reviewed for this project, whether or not it produces a spec or backlog change — a "no artifact produced" entry is still useful to prevent re-researching the same source later.
## Post-Quantum Cryptography Readiness — Known Future Consideration (08.08.2026)

**Source:** Yogeshkrishnanseeniraj, "Post-Quantum Readiness in Django: Preparing Your Encryption for the 2026 Security Standards," Medium, 03.03.2026.

**Status:** Not actionable now — logged as future consideration only.

**Key points:**
- NIST finalized FIPS 203 (ML-KEM/Kyber), FIPS 204 (ML-DSA/Dilithium), FIPS 205 (SLH-DSA/SPHINCS+) in August 2024.
- Threat model is asymmetric: "harvest now, decrypt later" (HNDL) makes confidentiality risk immediate even though quantum computers capable of breaking current crypto don't exist yet; signature-forgery risk is future/theoretical.
- Rational migration order per the article: fix key exchange first (cheap, immediate HNDL protection), defer signature migration (more expensive, more time available).
- Measured overhead (article's benchmarks): ML-KEM-768 vs classical X25519 ~3x on keygen/encapsulation; field encryption overhead ~2.2x on a full Django request (6.9ms vs 3.2ms) -- author notes DB queries, not crypto, remain the actual latency bottleneck for most Django apps.
- JWT token size tradeoff: ES256 ~180 bytes vs ML-DSA-65 ~4,400 bytes -- real cost if ever adopting PQC-signed JWTs.
- "Regulatory baseline" in the article applies to US federal contractors handling federal data by mid-2026 -- not applicable to this project.

**Why not actionable now:**
- This project has no federal/regulated data, and auth goes through MSAL/Entra CIAM, not self-issued JWTs.
- No compliance mandate currently requires PQC readiness at this project's scale.

**Where this becomes relevant:** if/when the project forks into CompliGuard (NIS2 compliance SaaS for DACH SMBs), EU regulatory direction on PQC-readiness for critical infrastructure may make this a real requirement, not just a research note.

**Cheap idea if ever revisited:** an `audit_crypto`-style management command (in the spirit of the article's own tool) to inventory where RSA/ECDH is actually used across TLS/JWT/field-encryption before any migration decision -- same "verify current exposure before deciding" principle already applied to the RBAC over-privilege audits (25-27.07.2026 sessions).

## ATT&CK Intelligence View for Detection Engineering (10.08.2026)

**Source:** Shahrukh Khan, "ATT&CK Intelligence View for Detection Engineering," Medium, 26.06.2026. Tool: mitre.heyshahrukh.me (community project, not an official MITRE product).

**Core takeaway:** Formalizes the chain `Technique -> Detection Strategy -> Analytic -> Mutable Elements -> Telemetry -> SIEM Rule`, with two ideas directly applicable here:
- **Data Source vs Data Component** distinction -- "where the log comes from" vs "which event type/fields inside it" -- and the resulting **telemetry gap vs detection gap** framing (missing log feed vs missing rule logic).
- **Mutable Elements** -- explicitly documented, named tuning parameters per analytic (e.g. `CommandLinePattern`, `TimeWindow`, `UserContext`), so the reasoning behind a detection's tuning survives past the engineer who wrote it.

**Comparison against this project's Security Dashboard (`security/mitre/attack_data.json`):**

| Criterion | ATT&CK Intelligence View | This project |
|---|---|---|
| ATT&CK data | Live Enterprise v19.1 | Static, hand-curated (20 techniques, 9 tactics) |
| Technique structure | Full 6-stage chain | Flat status field (mitigated/detected/monitored/gap) |
| Data Source / Data Component | Explicit, linked filters | Absent before this session |
| Mutable Elements | Documented table per analytic | Absent before this session |
| Threat Actor mapping | Built-in filter | Absent |
| Live alerts | None (reference tool only) | Present -- /security/alerts/ pulls live Defender for Cloud alerts via MSI |
| Verified-state discipline | N/A | Project's own strength -- e.g. already-flagged T1567 misclassification (RiskScoringMiddleware doesn't exist as real code) |

**Produced:** Added an optional `detection_engineering` block (`sentinel_rule`, `data_sources`, `data_components`, `mutable_elements`) to `security/mitre/attack_data.json`, populated for exactly the 4 techniques (T1078, T1036, T1595, T1046) backed by the project's two real, deployed Sentinel rules (`zero-trust-device-verification`, `defender-active-scanning-nmap`) -- deliberately not extended to any gap/planned technique, consistent with the honest-documentation principle. A `_schema_note` field documents this scope decision in the JSON file itself.

**Not done, flagged only:** T1595's `status: "gap"` sits alongside a real, working detection (Defender kernel-level + the Sentinel rule) -- the article's telemetry-gap/detection-gap distinction shows this is correctly "gap" at the *control* (prevention) level, not the detection level; a `status_note` field was added to that entry to make this explicit rather than changing the status. Separately (pre-existing, not from this article): T1567's `status: "detected"` still cites `RiskScoringMiddleware`, which per earlier sessions does not exist as real code -- left untouched pending a deliberate decision on that misclassification, not silently corrected here.

---

## Setting Up an Agentic AI Workflow with Claude Code (13.08.2026)

**Source:** Nikky Juwe, "Setting Up an Agentic AI Workflow with Claude Code," Medium, 04.08.2026. A seven-part DevOps course exercise (CLAUDE.md, Skills, Subagents, MCP, Hooks, Permissions, Memory) built around a small static HTML/CSS-to-Terraform-on-AWS example project.

**Core takeaway:** treats Claude Code like onboarding a new hire -- narrow tool access per task, specialists with isolated context instead of one general-purpose agent, guardrails that intercept dangerous intent before execution (not after), and a curated (200-line-capped) memory file instead of re-explaining rules every session. Central thesis: "calibration first, automation second."

**Comparison against this project actual working process:**

| Component | Article pattern | This project |
|---|---|---|
| Project context for the AI | Single CLAUDE.md, 5 sections | Split across docs/specs/CONSTITUTION.md, TEMPLATE.md, and conversation memory |
| Skills (scoped slash-commands) | 4 skills with explicit allowed-tools (e.g. tf-plan: Bash/Read/Grep, no Write) | None -- all Terraform work goes through manually copy-pasted bash commands in chat |
| Subagents (isolated-context specialists) | security-auditor (no Write), cost-optimizer (Haiku), tf-writer (inherit model) | None in Claude Code -- AI PR Review on GitHub Actions plays a similar read-only role as an external CI gate |
| MCP (live external data) | GitHub MCP, .mcp.json (team) vs settings.local.json (personal token, gitignored) | Not used -- all live Azure access goes through manual az rest calls and SSH sessions |
| Hooks (pre-execution guardrails) | UserPromptSubmit blocks destructive intent; PreToolUse blocks dangerous commands (terraform destroy, aws s3 rm) before execution | None technical -- guardrails are conversational discipline only |
| Permissions (allow/deny lists) | Explicit settings.json allow-list + deny-list | None configured |
| Cross-session memory | MEMORY.md, capped at 200 lines, curated | Claude.ai built-in memory system -- same goal, different mechanism |

**Produced:** This note only -- no code or config changes. Logged as input to a future backlog decision, not acted on immediately.

**Not done, but concretely worth prioritizing:** three gaps directly relevant to this project actual failure modes seen in recent sessions:
1. PreToolUse-style hook for Terraform/Azure destructive commands -- would have technically enforced what was, until now, purely human vigilance (e.g. the 10.08.2026 near-miss where a malformed local.auto.tfvars almost set the PostgreSQL admin password to the literal string "null").
2. Skills for the recurring tf-plan/tf-apply cycle, scoped without Write access for the plan step -- would remove the repeated manual bash-copy-paste pattern (and its recurring heredoc/bash-history-expansion breakage) seen across recent sessions.
3. An Azure MCP server, if one exists with adequate read scope -- would replace repeated manual az rest calls and SSH sessions with structured, repeatable queries.

None of these are spec ed yet -- per docs/specs/TEMPLATE.md triage section, hooks/skills would likely warrant a brainstorm pass before a full spec, since the right scope is not fully settled yet.

---

## DevSecOps Governance Part 3: Implementing DAST in Build Pipelines (13.08.2026)

**Source:** Wayne Campbell, "DevSecOps Governance (Part 3): Implementing Dynamic Application Security Testing (DAST) in Build Pipelines," Capgemini Microsoft Blog / Medium, 30.06.2026. Part 3 of a 3-part series on Azure DevOps pipeline governance.

**Core takeaway:** OWASP ZAP post-deployment, with an explicit authenticated-scanning step (Playwright browser-login generates a session cookie, passed into the ZAP container) and a deliberate fail-gate that only blocks the pipeline on High severity findings, warns on Medium. A versioned dast-plan.yaml declares spider duration, active-scan timeout, and exit-status thresholds as configuration, not hardcoded pipeline logic.

**Comparison against this project actual DAST job (verified by reading .github/workflows/deploy-staging-terraform.yml directly, not assumed from the green checkmark):**

| Aspect | Article pattern | This project (verified 13.08.2026) |
|---|---|---|
| Scan type | activeScan (attempts real attack payloads: SQLi, XSS, etc.) | zaproxy/action-baseline -- passive scan only, no active attack attempts |
| Authentication | Explicit Playwright login step, session cookie passed to ZAP via AUTH_HEADER | None -- scans as an anonymous visitor; everything behind CIAM/Google OAuth2 login (/security/, /finops/) is never reached |
| Fail gate | Explicit High=fail, Medium=warn thresholds in dast-plan.yaml | fail_action: false -- the job never fails the pipeline regardless of findings; SARIF is uploaded to the Security tab but nothing blocks deploy |
| Scan config | Versioned dast-plan.yaml, reviewable in PRs | No equivalent file -- only .zap/rules.tsv (baseline rule exceptions), no plan/timeout/threshold config |

**Produced:** This note only -- no code or config changes. The verification itself (reading the actual workflow file rather than trusting the green checkmark) is the main output: it corrected an implicit assumption that DAST -- OWASP ZAP passing meant meaningful security coverage was happening.

**Not done, flagged as a real coverage gap, not hypothetical:** the current DAST job provides materially weaker coverage than its green checkmark implies -- passive-only, unauthenticated, non-blocking. Logged as a new docs/backlog-status.md item and cross-referenced into the existing (Draft) security-md-honest-limitations.spec.md, since this is exactly the kind of gap that spec exists to surface rather than let a passing CI badge silently imply.
