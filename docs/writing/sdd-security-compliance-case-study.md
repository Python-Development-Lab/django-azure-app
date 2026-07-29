# Spec-Driven Development in a Solo Security-Engineering Project: What Actually Happened When I Applied It to a Compliance-Heavy Codebase

*A case study from `django-azure-app` — a production-grade Azure security template built for AZ-500/SC-200/SC-100 certification practice.*

---

## Why this is different from most SDD case studies

Most Spec-Driven Development content online — and there's a lot of it in 2026 — is written from a generic software-engineering perspective: build a CRUD API, wire up a stateful agent, ship a SaaS feature. The lessons are real, but they're about *code correctness*. Security and compliance work has a different failure mode, and it's worse: **a wrong assumption doesn't just break a feature — it creates false assurance.** A dashboard that shows "6 mitigated / 8 detected / 1 monitored / 5 gap" when the real number is "6/5/1/8" isn't a cosmetic bug. It's a security posture claim, made confidently, that happens to be wrong — the exact failure mode compliance frameworks exist to prevent.

This is what I found out, in one day, applying SDD for the first time to a project that already had 34 real ISO 27001 control records, a live MITRE ATT&CK coverage matrix, active Sentinel detection rules, and a Microsoft Defender for Cloud Secure Score — not a toy app, a system already making security claims about itself.

## The setup

The project: a Django application on Azure, built with a genuine Zero Trust architecture (Managed Identity everywhere, Key Vault for secrets, VNet isolation), a 7-job DevSecOps pipeline, Microsoft Sentinel detection rules, a live Security Dashboard rendering ATT&CK coverage and Defender alerts, and — this part matters — a full ISO 27001:2022 Annex A compliance-mapping system already in production, parsing 34 markdown control records into a live dashboard panel.

Before this session, none of it had a formal specification. Backlog items lived as prose. Decisions lived in memory. It worked, in the sense that the application ran — but there was no single, checkable contract for what any of it was actually supposed to do.

## What I built in one session

- A spec template (10 sections: Overview, Problem Statement, Scope, Data Model, Requirements in EARS notation, Non-Functional Requirements, Task Breakdown, Acceptance Criteria, Open Questions, Traceability) plus a Revision Log and a post-implementation Requirement Traceability Verification table.
- EARS notation (Easy Approach to Requirements Syntax) — a 2009 Rolls-Royce/aerospace requirements standard, now resurfacing in AI coding tools like AWS Kiro. Five fixed sentence patterns (Ubiquitous, Event-driven, State-driven, Unwanted behavior, Optional feature) that force unambiguous requirements instead of prose.
- Three persistent tracking files that turned out — independently, before I checked — to match a pattern used by several named AI-coding memory frameworks: a backlog-status tracker, a specs index, and a research-notes registry. Nobody told me to build these three specific files; I built them because a long working session without them kept losing context, and only later found out this is a recognized category of solution ("Memory Bank" pattern), not something I'd invented.
- A retroactive "baseline spec" pattern: instead of only writing specs for *future* work, I also wrote one documenting the *already-built* Security Dashboard as a formal, checkable contract — closing the gap between "code exists" and "code is specified."
- An independent-reviewer subagent definition (read-only tools, explicit instruction not to edit files) — built, but not yet exercised in practice, which I'm noting here rather than pretending otherwise.

By the end of the day: 9 formal spec documents, three living trackers, and one uncomfortable discovery repeated five times.

## The five catches — in order, with receipts

**1. The wrong threat-intelligence table.** A spec assumed a Sentinel table called `ThreatIntelligenceIndicator` was empty, concluding a planned IOC-reputation feature had no data source. A direct query proved the table was real, but *deprecated by Microsoft since July 2025* — the actual live table, `ThreatIntelIndicators`, was fully populated with high-confidence indicators from an active Microsoft Defender Threat Intelligence connector. The spec had queried the wrong noun.

**2. The schema that wasn't what three documents assumed.** Multiple specs — and the project's own long-standing documentation — assumed `attack_data.json` was a flat list of techniques with a `technique_id` field. A direct read of the file showed a nested `tactics[].techniques[].id` structure. Worse: the project had been citing "6 mitigated / 8 detected / 1 monitored / 5 gap" for weeks. The real file, counted by hand against the schema that actually existed, showed **6 / 5 / 1 / 8** — three additional gap techniques the project's own summaries had never mentioned, all tied to a middleware component that (per an earlier session) doesn't actually exist as code yet.

**3. A status that directly contradicted new evidence.** One technique (`T1552`, unsecured credentials) was already marked "mitigated" in the live file, based on Key Vault + Managed Identity being in place. A newly-discovered Critical attack path showed that same control was *currently bypassable* via an outdated cryptography dependency. The honest resolution wasn't to silently overwrite the status — it was to flag the conflict explicitly as an open decision, and argue for "gap" over "mitigated" on the grounds that a control under live compromise shouldn't be marked as working.

**4. The compliance document that could have silently broken its own dashboard.** A shared-responsibility document, written earlier the same session and placed in the ISO 27001 records directory, contained markdown horizontal rules (`---`) that the project's own compliance-parser — which splits files on exactly that character — would have misread as malformed frontmatter. It likely wouldn't have thrown an error. It would have quietly inflated the "total controls" count on a live dashboard with one meaningless entry. Caught by reading the parser's actual code before assuming the new file was harmless.

**5. A quantified claim that turned out to be about the wrong project.** Microsoft Defender's Secure Score showed 36%, with "Remediate vulnerabilities" as the single largest weighted gap (0 of 6 points). It seemed obvious: this had to be the project's own known, unpatched dependency vulnerability. A direct API query of the actual unhealthy assessments showed every single one belonged to a *different project* sharing the same Azure subscription. The intuitive fix — "patch the dependency, watch the score jump from 36% to 67%" — was very likely wrong, caught only by insisting on resource-level verification instead of category-name matching.

## What's actually different about doing this in a security/compliance context

Three things, none of which show up in generic "AI coding agent" SDD writing:

**A wrong assumption here isn't a bug, it's a false assurance claim.** A CRUD endpoint that silently does the wrong thing fails a test. A compliance dashboard that silently overcounts "implemented" controls, or a coverage matrix that silently overstates detection coverage, produces a document someone might actually rely on to make a real security decision — or cite in a certification, or an audit, or an interview.

**Pre-existing artifacts carry the same risk as pre-existing code, and this domain has more of them.** Threat models, incident-response playbooks, Architecture Decision Records, and compliance records are all "prior work" in exactly the sense a codebase is — and in this project, four different categories of them existed, undocumented in any tracker, discovered only by checking the filesystem directly rather than trusting the backlog's own "not started" label. A generic software project rarely has this much pre-existing analytical work sitting untracked; a security program built up over months usually does.

**The verification target is broader than "does the code work."** In application development, verify-before-lock usually means "does this match the API/library's real behavior." Here it also meant: does this match the real MITRE ATT&CK classification, the real ISO 27001 control text, the real Azure resource ownership boundary, the real ownership boundary between projects sharing a subscription. Each of the five catches above was a different *kind* of fact to get wrong, not the same mistake five times.

## The honest parts — what this didn't magically fix

- The methodology's own biggest gap — running an explicit "explore the codebase before writing the spec" step, the single change that would likely have prevented catch #2 and #4 before they happened rather than after — is still a recommendation in a template file, not an enforced practice. It's been identified, not yet fixed.
- None of the 6 forward-looking specs written this session have been implemented yet. Every "post-implementation verification" table in every spec is still an empty placeholder. The methodology has been tested at the *specification* stage, not yet at the *does the resulting code actually match the spec* stage.
- A known, quantified security issue (a set of CVEs in an outdated dependency, already flagged by GitHub Dependabot) sat unexamined through the entire session that produced this article, despite being referenced by name multiple times. Knowing the right principle and acting on it in the moment are not the same thing, and this is worth admitting rather than editing out of the narrative.

## If you're doing something similar

- If your project already has compliance records, threat models, ADRs, or playbooks sitting in the repo, check for them with `find` and `git log --all` before writing a new spec for that area — don't trust your own backlog tracker's "not started" label without a filesystem check.
- Build your three memory files (a backlog/status tracker, a specs index, a source-registry) early — not because a framework told you to, but because a working session without them starts repeating research and re-deciding settled questions by hour three.
- When a spec makes a quantified claim ("this fix will improve score X by Y%"), verify the resource-level attribution before publishing the number, especially in any shared environment (a subscription, an org, a monorepo) where more than one project's data can end up in the same aggregate metric.
- Keep a Revision Log per spec, and write down *why* something changed, not just what changed. The reason is what stops the next session from re-making the same wrong assumption.

---

*This project's full spec set, including the methodology's own retroactive baseline spec (`docs/specs/sdd-methodology-baseline.spec.md`), the source registry (`docs/research-notes.md`), and the quantified metrics referenced above (`docs/backlog-status.md`), are part of the `django-azure-app` repository.*