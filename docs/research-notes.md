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

---

## DevSecOps Governance Part 1: Tooling, Secret Scanning, and Branch Protection (14.08.2026)

**Source:** Wayne Campbell, "DevSecOps Governance (Part 1): Tooling, Secret Scanning, and Branch Protection Strategies," Capgemini Microsoft Blog / Medium, 27.03.2026. Part 1 of the same 3-part series as the DAST article evaluated 13.08.2026.

**Core takeaway:** an Azure DevOps-specific governance model -- GitHub Advanced Security (secret scanning + SAST/SCA), Branch Policies (required reviewers, merge-type controls, force-push protection), Security Policies (fine-grained Allow/Deny/Not-Set permissions with hierarchy inheritance), and Pre-deployment Approvals -- an explicit human sign-off gate before deploying to a given environment, separate from PR review.

**Comparison against this project (verified directly via GitHub Settings -- Branches and Settings -- Environments, not assumed):**

| Aspect | Article pattern | This project (verified 14.08.2026) |
|---|---|---|
| Branch protection | Required reviewers, merge-type controls, force-push protection | None configured -- GitHub explicitly shows Classic branch protections have not been configured for any branch |
| Pre-deployment approval gate | Explicit Required reviewers step before deploying to an environment | staging environment exists with 1 protection rule shown, but Required reviewers and Wait timer are both unchecked -- the 1 rule is just the default all branches can deploy state, not an actual gate |
| Deployment branch restriction | Implied by branch policies | Deployment branches and tags is set to Protected branches only, but since no branches are actually protected (see above), this restricts nothing in practice |
| Admin bypass | Not discussed in the article | Allow administrators to bypass configured protection rules is checked on the staging environment -- would bypass even if reviewers were later added |
| Terraform apply trigger | N/A (article does not cover this) | Not unconditional -- gated by an idempotency check (needs.check-infra.outputs.infra_exists == false OR a manual force_terraform input), which is a real, useful guard, just not a human-approval gate |
| Secret scanning | GHAS-native, blocks push | Gitleaks CLI (separate tool, first CI job) -- scans on push/PR, does not block the git push itself the way GHAS push protection does |

**Produced:** This note only -- no code or config changes. Direct verification (Settings pages + workflow YAML, not memory or assumption) is the actual output, continuing the same discipline applied to the DAST finding yesterday.

**Not done, flagged as a real gap, not hypothetical:** this project currently has no technical deployment gate at all -- no branch protection, no required reviewers on the staging environment, and admin bypass enabled even if that were added. For a solo-maintainer portfolio project at this stage that is a reasonable, low-risk state in practice (the maintainer is the only person who merges or deploys), but it is a real gap between how the 7-job CI/CD pipeline presents itself ("DevSecOps pipeline") and what it technically enforces. Logged as a new docs/backlog-status.md item, and flagged as SECURITY.md Honest Limitations material alongside the DAST finding -- both are instances of the same underlying pattern: a passing pipeline or a configured-looking Environment implying more actual control than currently exists.

---

## DevSecOps Governance Part 2: SAST, SCA, and Build Pipelines (14.08.2026)

**Source:** Wayne Campbell, "DevSecOps Governance (Part 2): Static Analysis Software Testing (SAST), Software Composition Analysis (SCA) and Build Pipelines," Capgemini Microsoft Blog / Medium, 27.03.2026. Part 2 of the same 3-part series as the Part 1 (branch protection) and Part 3 (DAST) articles already evaluated.

**Core takeaway:** out-of-the-box GHAS SAST/SCA only produces passive, informational findings. To actually block insecure code, the pipeline must wire in explicit fail thresholds -- failOnSeverity/failOnAlerts for GHAS CodeQL/Dependency Scanning, and Checkov (a dedicated third-party tool, chosen specifically for its network-configuration checks -- VNets, NAT Gateways, NSGs, private endpoints) for IaC, with a centralized .checkov.yml declaring soft-fail for low/medium findings and documented skip-check exceptions.

**Comparison against this project (verified directly by reading .github/workflows/deploy-staging-terraform.yml, continuing the same discipline as the Part 1 and Part 3 comparisons):**

| Aspect | Article pattern | This project (verified 14.08.2026) |
|---|---|---|
| SAST (application code) | CodeQL, failOnAlerts true -- genuinely blocks the build | Bandit -- every invocation ends in double-pipe true, so the job can never fail regardless of findings |
| SCA (dependency scanning) | GHAS Dependency Scanning, failOnSeverity error | pip-audit -- also ends in double-pipe true, same non-blocking pattern |
| SAST (IaC) | Checkov, soft-fail only for low/medium, hard fail by default for High/Critical | Trivy, exit-code 0 explicitly set -- no severity split, nothing fails regardless of finding severity even at CRITICAL |
| Documented scan exceptions | Centralized .checkov.yml with a curated skip-check list and inline reasons | No equivalent file -- no trivyignore or documented rationale for any accepted finding |
| What actually blocks the pipeline today | SAST + SCA + IaC + (per article) DAST all configured to fail the build | Only Tests and Lint (coverage fail-under 70, flake8) -- every security-specific scanner (Bandit, pip-audit, Trivy, and per yesterday DAST finding, OWASP ZAP) is purely informational |

**Produced:** This note only -- no code or config changes.

**Not done, flagged as a real gap, not hypothetical -- and now a pattern, not an isolated finding:** this is the third consecutive day direct verification (not trusting a green checkmark) has found the same underlying issue in a different layer -- 13.08.2026: DAST is passive, unauthenticated, non-blocking; 14.08.2026 Part 1: zero deployment gate exists; 14.08.2026 Part 2, this note: none of the four security scanners (Bandit, pip-audit, Trivy, ZAP) can fail the pipeline -- only the unrelated Tests and Lint job can. The 7-job pipeline actual enforcement surface is narrower than its name (DevSecOps pipeline) implies across every layer checked so far. Given the recurrence, this is being logged as a single consolidated docs/backlog-status.md item covering all four scanners together (SAST/SCA/IaC/DAST severity-gate enablement) rather than one more isolated entry, and flagged as the primary SECURITY.md Honest Limitations content alongside the Part 1 and Part 3 findings.

## Cynet — "What Is Incident Response? Process, Practices & Automation" (vendor context, 2026)

**Джерело:** https://www.cynet.com/security-foundations/incident-response/what-is-incident-response/
**Тип:** vendor content (не академічне джерело, без DOI) — використовується лише як термінологічний reference, не як технічне обґрунтування рішень.

### Що взято на озброєння

**1. Термінологія Event → Alert → Incident**
Використати дослівно в `SECURITY.md` для класифікації даних з Sentinel:
- *Event* — зміна стану системи (напр. запис у `AzureDiagnostics`)
- *Alert* — сповіщення, що спрацювало на подію (напр. запис у `SecurityAlert`, 16 наявних записів: 15 Zero Trust + 1 NMap)
- *Incident* — подія, що реально становить ризик (наразі жоден з 16 alerts у проєкті формально не ескальовано до статусу incident — це важливо зафіксувати як чесний стан)

**2. SANS 6-phase vs NIST 4-step lifecycle**
- SANS: Preparation → Identification → Containment → Eradication → Recovery → Lessons Learned
- NIST: Preparation → Detection & Analysis → Containment/Eradication/Recovery → Post-Incident Activity
Обрати одну модель (рекомендація: SANS 6-phase — детальніша, краще лягає на "Honest Limitations" секцію) як структуру для `SECURITY.md` розділу Incident Response.

**3. Термінологічне уточнення для наявного backlog-пункту**
Backlog-пункт "Automated response: Logic App playbook → `POST /users/{userId}/revokeSignInSessions`" відповідає означенню **SOAR playbook** зі статті (automated incident response process, що виконує предефінований сценарій у відповідь на alert). Перейменувати/задокументувати цей компонент явно як SOAR-елемент — підсилює відповідність SC-200 domain (Security Orchestration, Automation and Response) і портфоліо-наратив.

### Gap-категорії, підтверджені цим джерелом (додатково до 5 ATT&CK gap techniques)

Проєкт наразі не має:
- **SOAR** — автоматизовані playbook-дії відсутні (є лише backlog-намір)
- **UEBA** — поведінкова аналітика користувачів відсутня; `zero-trust-device-verification` rule закриває лише частину (device fingerprinting, не behavioral baseline)
- **ASM** — немає безперервного сканування зовнішнього attack surface (WAF/Application Gateway з T1595 закриває суміжну, але не еквівалентну задачу)
- **Формальний IRP-документ** — ролі, комунікаційний план, ескалаційні процедури відсутні
- **CSIRT-модель** — не актуально для solo-maintainer проєкту; зафіксувати в `SECURITY.md` як "N/A — single maintainer, no formal CSIRT"

### Зв'язок із запланованим функціоналом

"Ask AI about this alert" панель (Claude API + knowledge graph контекст) відповідає підходу статті до GenAI в IR: LLM як co-pilot з людиною-аналітиком у контурі рішень (human-in-the-loop), а не автономний agent — це варто явно зазначити в дизайні панелі як усвідомлений архітектурний вибір.

### Висновок

Джерело не додає нового технічного know-how, але корисне як checklist для `SECURITY.md`: формалізує термінологію, підтверджує вже відомі прогалини (SOAR/UEBA/ASM) додатково до 5 ATT&CK gap techniques, і дає точну назву ("SOAR") для вже запланованого Logic App playbook пункту.

## appsecwarrior — "How To Secure Architecture Guide for Modern AI & Agentic Platforms" (Medium, 27.07.2026)

**Джерело:** https://medium.com/@appsecwarrior/how-to-secure-architecture-guide-for-modern-ai-agentic-platforms-400848022838
**Тип:** практична AppSec-стаття (не vendor content) — component-by-component secure reference architecture для агентних AI-систем + case study про broken access control в AI-агентах (Meta AI Account Takeover pattern).

### Що взято на озброєння

**1. OWASP Top 10 for LLM Applications — новий framework поряд з MITRE ATT&CK**
Наразі `security/mitre/attack_data.json` покриває лише класичний MITRE ATT&CK (20 технік/9 тактик), без LLM-специфічного шару загроз. Коли AI-функції ("Ask AI about this alert" панель, AI PR Review gate) перейдуть з планів у реалізацію — потрібен окремий шар загроз:
- Prompt injection, insecure output handling, training data poisoning, model DoS, supply chain, sensitive info disclosure, insecure plugin/tool design, excessive agency, overreliance, model theft
- Принцип: будь-який контент, який LLM читає (user input, retrieved documents, tool output, повідомлення іншого агента) — це **untrusted input**, незалежно від джерела

**2. "Maze Design" — 7-gate модель контролю привілейованих дій (найцінніша частина статті)**
Case study (Meta AI Agent Account Takeover) показує клас вразливості: агент витягує параметри з plain text і викликає привілейований tool без перевірки ownership. Запропонована модель — послідовні gates, кожен з яких має пройти незалежно:
1. Intent classification (privileged vs read-only)
2. Identity/authentication
3. Ownership (чи належить ресурс саме цьому requester)
4. Capability scope (чи може tool взагалі мутувати дані)
5. Policy engine (чи дозволяє policy цю дію explicitly)
6. Rate limiting/abuse detection
7. Step-up verification (token/MFA/verified channel)

Принцип: **жоден єдиний шар не повинен мати прямий шлях від "агент зрозумів запит" до "виконана привілейована мутація"**. Fail closed за замовчуванням: unknown tool → deny; unknown policy → deny; ambiguous parameters → deny.

**3. Пряме застосування до запланованого backlog-пункту**
Backlog-пункт "Automated response: Logic App playbook → `POST /users/{userId}/revokeSignInSessions`", якщо в майбутньому буде тригеритись через AI-рекомендацію (а не лише через Sentinel rule напряму) — підпадає під точнісінько цей клас ризику. Якщо "Ask AI about this alert" панель колись зможе не просто пропонувати fix, а й ініціювати дію — це вимагає тих самих gates, а не "AI порадив → виконали".

**4. MCP-специфічні поради (розділ 3.5 статті) — релевантно для майбутньої MCP-інтеграції**
- Підключення лише до pinned/vetted MCP-серверів (версії/хеші зафіксовані, як будь-яка third-party залежність supply chain)
- Per-tool authorization — перевіряється саме identity, що викликає tool, а не факт "агент має доступ до tool"
- Секрети для MCP-tools — з secrets manager, ін'єктовані в runtime, ніколи не в tool config чи prompt тексті
- Sandbox tool execution, захист від SSRF у tools, що фетчать URL

**5. Параметрична плутанина (parameter confusion) — конкретний технічний нюанс**
Авторитетне попередження: поле, яке перевіряє policy (напр. `username`), і поле, на яке діє tool (напр. `account_id`), мають бути **тим самим resolved identifier**, а не двома окремо витягнутими значеннями з тексту. Інакше перевірка ownership пройде, а дія виконається над іншим ресурсом.

### Gap-аналіз для `threat-model-agent` (Security-Engineering-Lab/threat-model-agent)

- ❌ `stride_engine.py` наразі оперує класичним STRIDE, без LLM-adjacent категорій загроз (prompt injection, excessive agency тощо) — варто розглянути розширення на OWASP Top 10 for LLM Applications як другий шар аналізу
- ⚠️ **Перевірити**, як саме зберігається `ANTHROPIC_API_KEY` в проєкті — чи через змінні середовища, чи (небажано) захардкоджено в конфіг-файлах. CLI-tool сам по собе не виконує привілейованих мутацій (лише read + report), тому ризик Maze Design тут нижчий, але secrets-hygiene залишається актуальною
- 📋 Логування рішень `attack_mapper.py`/`report_generator.py` як окремого audit trail — наразі не задокументовано як практика

### Gap-аналіз для `django-azure-app`

- 📋 "Ask AI about this alert" панель — на етапі дизайну, ще до імплементації. Рекомендація: явно спроєктувати як **Design 3 (centralized policy layer)**, а не Design 1/2 — тобто LLM лише класифікує/рекомендує, а виконання (якщо колись з'явиться) проходить через окремий policy engine з fail-closed за замовчуванням
- 📋 AI PR Review gate — вже задокументовано як "informational only — no auto-merge", що фактично відповідає Design 1 (агент ніколи не виконує mutation напряму) — це правильний архітектурний вибір з коробки, варто explicitly зазначити цей rationale в специфікації фічі
- ❌ Rate limiting / abuse detection на виклики до Claude API — не задокументовано в жодному з двох проєктів

### Висновок

На відміну від Cynet-статті, це джерело дає конкретний, придатний до застосування архітектурний патерн (Maze Design) саме в момент, коли AI-функції проєкту ще на стадії планування — ідеальний час інтегрувати ці gates у дизайн, а не патчити пост-фактум. Найвищий пріоритет: коли розпочнеться реалізація "Ask AI about this alert" панелі, явно задокументувати в specs/ADR, що вона архітектурно відповідає Design 1 (agent never performs mutation directly) з поясненням rationale.

## Younes Khaldi — "How to Use Azure Sentinel for Incident Response, Orchestration and Automation" (LinkedIn/Microsoft Community Hub, 29.03.2021)

**Джерело:** https://www.linkedin.com/pulse/how-use-azure-sentinel-incident-response-automation-younes-khaldi/ (дзеркало: Microsoft Community Hub, той самий автор і зміст — LinkedIn блокує прямий automated-доступ)
**Тип:** практична стаття практикуючого security-інженера, доповнена перевіркою актуальності через офіційну документацію Microsoft Sentinel (Learn/Azure Docs). Сама стаття застаріла на 5 років (написана під бренд "Azure Sentinel", нині "Microsoft Sentinel"), але описаний use case і термінологія залишаються чинними.

### Що взято на озброєння

**1. Automation rules vs Playbooks — архітектурна різниця, якої бракує в проєкті**
- *Automation rules* — прості дії без Logic Apps: тригаж severity, assign owner, suppress noisy incidents, auto-close known false positives, tag classification
- *Playbooks* (на базі Azure Logic Apps) — складніші дії з інтеграцією зовнішніх сервісів (ServiceNow tickets, email notifications, isolation/revocation actions)

**Ключовий gap:** у проєкту є детекція (3 analytics rules) і є план на playbook (`revokeSignInSessions`), але **відсутній проміжний automation rules шар**. Без нього 16 наявних `SecurityAlert` записів не мають механізму autotriage — накопичуються без owner assignment чи suppression правил.

**2. Офіційний reference pattern "stop potentially compromised users"**
Microsoft Learn документує саме той сценарій, що вже в backlog проєкту: automation rule тригериться на incident creation → викликає playbook → playbook виконує revocation/isolation дії. При імплементації `revokeSignInSessions` playbook варто звірятись з цим офіційним tutorial (https://learn.microsoft.com/en-us/azure/sentinel/automation/tutorial-respond-threats-playbook), а не проєктувати структуру з нуля.

**3. Microsoft Sentinel Automation Contributor role**
Коли playbook буде реалізовано, Sentinel використовує окремий service account для запуску playbooks на incidents — цьому service account потрібна власна роль **Microsoft Sentinel Automation Contributor** на resource group, де лежить Logic App (окремо від звичайних user/CI ролей). Це варто врахувати при RBAC-плануванні playbook-реалізації.

**4. Threat intelligence feed enrichment (з оригінальної статті, нижчий пріоритет)**
Автор демонструє імпорт threat indicators з AlienVault OTX через Graph Security API в нативну Sentinel-таблицю `ThreatIntelligenceIndicator`, з кореляцією через Microsoft Defender for Endpoint дані. Не застосовується напряму до проєкту — Defender for Endpoint призначений для VM/endpoint-навантажень, а проєкт використовує Defender for App Service (PaaS-рівень) — інша модель захисту. Залишити як довгостроковий, низькопріоритетний concept, якщо колись з'явиться потреба в зовнішніх threat intel feeds.

### Критичний факт, знайдений під час перевірки актуальності (не зі статті)

**Microsoft Sentinel Portal deprecation:** після **31 березня 2027** Microsoft Sentinel більше не підтримуватиметься в Azure Portal і буде доступний лише в Microsoft Defender Portal. Усі користувачі Azure Portal-версії Sentinel будуть автоматично перенаправлені в Defender Portal.

**Релевантність для проєкту:** Sentinel-конфігурація (`law-django-azure-staging`, 3 analytics rules, Data Connector) наразі керується частково через Terraform, частково через `az rest` manual artifacts (діагностичні налаштування Key Vault/PostgreSQL). Варто зафіксувати як довгостроковий tracked item — переконатись, що жодна частина конфігурації не залежить від Azure Portal-специфічного UI/API, який припинить підтримку, і що Terraform-модуль `monitoring` сумісний з Defender Portal API поверхнею. Термін некритичний (2027), але вартий одного review-циклу протягом наступного року.

### Gap-аналіз для `django-azure-app`

- ❌ **Automation rules — відсутні повністю.** Найвищий пріоритет із цього джерела: почати з простих правил (assign severity/owner на `zero-trust-device-verification` alerts, auto-close known false positives для NMap-сканів з відомих Azure IP-діапазонів) — реалізовується швидше і незалежно від повноцінного Logic App playbook
- 📋 Sentinel Automation Contributor role — додати до RBAC-плану, коли `revokeSignInSessions` playbook перейде з backlog у реалізацію
- 📋 Sentinel Portal deprecation (2027) — новий довгостроковий tracked item, review протягом наступного року
- N/A Threat intel feed enrichment (AlienVault OTX) — не застосовується до поточної архітектури проєкту, залишити як concept без пріоритету

### Висновок

На відміну від двох попередніх статей (Cynet — термінологія; appsecwarrior — архітектурний патерн для AI-агентів), ця стаття дає **конкретний, реалізовуваний наступний крок**: automation rules — це найшвидший спосіб частково закрити SOAR-gap (задокументований і в Cynet, і тут) ще до того, як `revokeSignInSessions` playbook буде повністю готовий. Також виявлено новий, раніше не зафіксований довгостроковий ризик — Sentinel Portal deprecation у 2027 році.

## Team Axon (Hunters.security) — "The Human-Friendly Guide: IR & Threat Hunting in Microsoft Azure, Part 1" (Alon Klayman)

**Джерело:** https://www.hunters.security/en/blog/human-friendly-guide-incident-response-microsoft-and-threat-hunting-azure-1
**Тип:** практичний технічний guide від Threat Hunting Expert, з повним кейс-стаді розслідування (сценарій "HNTR-Global").

**Ключове:**
- Azure IR спирається на 3 основні джерела логів: **Sign-in Logs** (30 днів), **Audit Logs** (30 днів, зміни в Azure AD), **Activity Logs** (90 днів, зміни на рівні subscription/resources) — рекомендація форвардити в SIEM, не покладатись на дефолтний retention
- **Gotcha:** IP-адреса в Audit Logs іноді показує внутрішню Microsoft IP замість реальної IP атакуючого — важливо не сплутати з IOC
- RBAC-нюанс: Azure Roles (RBAC) і Azure AD Roles — два незалежні набори прав, що не перетинаються автоматично; Global Admin може self-elevate до User Access Administrator на root scope

**Gap для проєкту:**
- ❌ **Azure AD Audit Logs та Activity Logs не форвардяться в Sentinel взагалі** — лише Sign-in Logs у планах (CIAM pipeline pending). Це напряму стосується вже відомого RBAC-issue (`django-azure-sp` на subscription scope, Contributor + User Access Administrator) — саме Activity Logs були б головним джерелом розслідування, якби через цей over-scoped SP стався інцидент
- 📋 Зафіксувати IP-адреса gotcha до запуску CIAM SigninLogs pipeline

---

## Sygnia — "Incident Response to Cloud Security Incidents: AWS, Azure, and GCP Best Practices" (оновлено 15.07.2026)

**Джерело:** https://www.sygnia.co/blog/incident-response-to-cloud-security-incidents-aws-azure-and-gcp-best-practices/
**Тип:** vendor-контент від авторитетного DFIR-провайдера (4х Gartner DFIR Market Guide), 5-фазний Cloud IR framework на базі NIST SP 800-61, окремі best practices для AWS/Azure/GCP.

**Ключове:**
- Azure-специфічно: "Sentinel playbooks for instant action — block sign-ins from suspicious IP ranges, disable compromised accounts" — конкретні типи дій для SOAR-playbook, ширше за вже заплановий `revokeSignInSessions`
- IR readiness метрики: **MTTR** (Mean Time to Respond/Recover), **Dwell time**, **Cost per incident**, **Post-incident hardening rate** (скільки lessons learned реально впроваджено наступного кварталу)

**Gap для проєкту (підтверджує вже відомий third-party-джерелами):**
- ❌ Sentinel playbooks / automation rules — **третє незалежне джерело поспіль** (після Cynet і Younes Khaldi), що фіксує ту саму прогалину — стійкий, підтверджений сигнал, не випадковість
- ❌ MTTR/Dwell time — жодна попередня research-note не згадувала формальне вимірювання; варто розглянути простий tracking у `docs/backlog-status.md` для майбутніх incident-подій (кількісний доказ для портфоліо)

**Висновок для обох джерел:** Разом з Younes Khaldi-нотаткою це дає повну картину Sentinel SOAR-gap: детекція є, Sign-in Logs у планах, але Audit/Activity Logs, automation rules і playbooks — усі відсутні. Коли дійде до OIDC/RBAC-scoping задачі (backlog #2), варто одночасно додати forwarding Activity Logs — саме вони покажуть аудит-слід тих RBAC-змін, що плануються.
