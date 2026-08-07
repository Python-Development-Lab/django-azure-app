# Security Cost Register

Purpose: make explicit, for each significant security control in this
project, what it costs, what risk it closes, and why the current tier/choice
is proportionate to a single-region staging-scale template -- not a larger
enterprise deployment. This is a living document; update it whenever a
security-relevant infrastructure choice is made or revisited.

Format follows the same spirit as `docs/adr/` (Чому / Альтернатива), but
scoped specifically to cost-vs-risk trade-offs across the whole stack,
not one decision at a time.

## Summary table

| Control | Monthly cost (approx) | Risk it closes | Tier chosen | Why this tier is proportionate |
|---|---|---|---|---|
| Azure App Service Plan | ~$13 (B1) | Availability, compute isolation | B1 (Basic) | Single staging instance, no autoscale/SLA requirement yet. Premium tier (~$70+/mo) would buy VNet integration we already get free on B1 via regional VNet integration, plus features (deployment slots beyond 1, autoscale) not needed at current traffic. |
| Microsoft Defender for Cloud | Standard tier, ~$15/server-month equivalent for App Service | Runtime threat detection (confirmed: NMap scan alert, 2026-06-26) | Standard (not Premium/CSPM add-ons beyond default) | Standard tier already delivers the control that mattered in practice -- a real detected attack. Premium adds agentless VM scanning and container-specific features not applicable here (no VMs, no AKS in this project). |
| Microsoft Sentinel | Pay-per-GB ingested, currently low volume (single App Service + Key Vault + PostgreSQL diagnostic logs) | Centralized detection, correlation, incident visibility | Default ingestion, no dedicated Log Analytics Dedicated Cluster | Dedicated Cluster commitment tiers (~$730+/day minimum) are enterprise-scale; this project's log volume is nowhere near the break-even point. Revisit only if ingestion grows an order of magnitude. |
| Key Vault | ~$0.03/10k operations + $1/certificate-month (none in use) | Secrets-at-rest protection, Managed Identity access | Standard tier, Private Endpoint | Standard tier (not Premium/HSM-backed) is sufficient -- no compliance requirement here mandates HSM-backed keys (FIPS 140-2 Level 2). Premium would roughly double cost for a guarantee this project doesn't need yet. |
| Azure Firewall (WAF layer, T1595 gap) | Not yet deployed -- estimated ~$0.025/hour (~$18/mo) + WAF policy for Application Gateway v2, vs. Azure Front Door Premium (~$330/mo minimum) | Web-layer attack surface (currently an open ATT&CK gap: no IP/WAF restriction on `/auth/login/`) | **Decision: Application Gateway v2 + WAF**, not Front Door | Front Door is a global edge service justified by multi-region/global-audience needs -- not applicable to this single-region (West Europe), single-backend deployment. Application Gateway is regional and integrates directly into the existing VNet/subnet architecture at a fraction of Front Door's cost. See backlog note (24.07.2026) for full reasoning. Deferred to CompliGuard fork if DACH-wide reach ever requires Front Door's capabilities. |
| NAT Gateway | Not deployed -- ~$32/mo (gateway) + data processing | Predictable, single outbound IP for allowlisting on external services | **Decision: deferred** (ADR 0002) | App Service's built-in Standard SNAT already provides working outbound connectivity with no NAT Gateway. The only reason to add one is to collapse the current 14 unpredictable outbound IPs into one stable IP for external allowlisting (e.g. Neo4j Aura). Paying for this before it's needed would be provisioning "just in case." Revisit specifically when Security Dashboard Phase 2 (Neo4j Aura) starts. |
| DevSecOps pipeline tooling (SAST/DAST/SCA) | $0 | Code-level vulnerability detection, secret leakage, dependency CVEs, dynamic app scanning | Bandit, Gitleaks CLI, pip-audit, Trivy, CycloneDX, OWASP ZAP -- all open-source/free | Commercial equivalents (Snyk, Veracode, Checkmarx) offer marginally better UX and enterprise reporting, but the underlying detection coverage (SAST, secrets, SCA, DAST) is functionally equivalent for a project this size. Free tooling closes the same ATT&CK-relevant gaps at zero licensing cost -- the trade-off is engineering time to wire SARIF output manually (already paid, see `scripts/gitleaks_to_sarif.py`, `scripts/zap_to_sarif.py`), not ongoing dollars. |
| AI PR Review (Claude API) | Pay-per-token, low volume (one review per PR, advisory-only) | Catches unintended permission changes, convention drift, logic issues deterministic scanners cannot see | Claude Sonnet, single review pass, no auto-merge/autonomous remediation | Deliberately scoped below Devin-style fleet automation (see 05.08.2026 backlog note) -- that tier of automation is priced and justified for many-repo, high-finding-volume organizations, not a one-person repository. One review per PR keeps token cost trivial while still closing a real gap (already found: an unnecessarily broad `Key Vault Administrator` role grant on 05.08.2026). |
| Application Insights / Log Analytics | Pay-per-GB, currently minimal (single app, low traffic) | Observability, exception visibility, incident diagnosis | Default retention, no Log Analytics Dedicated Cluster | Same reasoning as Sentinel above -- default consumption pricing is appropriate at this log volume. Notably, this control had a real 3-week outage (19 Jul - 6 Aug 2026, root-caused to a startup race condition) that cost nothing in cash but cost real diagnosis time -- a reminder that "cheap" and "reliable" are separate axes, not the same trade-off. |

## Explicitly deferred controls (not a gap -- a scoped decision)

These are controls a larger deployment would need but this project
deliberately does not implement, because the cost would not be proportionate
to the risk at current scale:

- **Multi-region failover / Front Door global load balancing** -- single-region template, no global audience yet. Revisit only at CompliGuard fork if DACH-wide multi-region reach becomes a real requirement.
- **Log Analytics Dedicated Cluster / commitment tiers** -- log volume orders of magnitude below the pricing break-even point.
- **Key Vault Premium (HSM-backed keys)** -- no compliance mandate (e.g. FIPS 140-2 Level 2) currently applies to this project.
- **Defender for Cloud Premium/CSPM add-ons beyond Standard** -- agentless VM scanning and Kubernetes-specific features do not apply; this project has no VMs or AKS.

## Explicitly NOT deferred -- known open gap

- **WAF/IP restriction (T1595)** -- unlike the deferred items above, this is a real, currently-open ATT&CK gap (confirmed NMap scan reached `/auth/login/` on 2026-06-26) with a chosen, costed solution (Application Gateway v2 + WAF) that has not yet been implemented. This belongs in the backlog as the highest-priority security cost decision still pending action, not a permanently accepted risk.

## How to use this document

When proposing a new security control or reconsidering an existing one:

1. State the risk it closes in ATT&CK-technique or CIS-control terms where possible (this project already maintains a 20-technique coverage matrix in `security/mitre/attack_data.json` -- reference it).
2. State the monthly cost at current scale, not list price alone.
3. State the next-tier-up cost and what additional capability it buys, so "why not the bigger tier" has an explicit answer.
4. If deferring, name the concrete trigger condition that should prompt revisiting the decision (as done above for NAT Gateway and Front Door).

This keeps every control's inclusion or exclusion defensible in a review,
an audit, or an interview -- the same standard already applied informally
via `docs/adr/` decision records, just centralized into one place for
side-by-side cost comparison.
