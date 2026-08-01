# Security Policy — django-azure-app

## Introduction

This document describes the security posture of `django-azure-app`, a production-grade Azure web application security template built as a hands-on portfolio artifact and certification vehicle (AZ-500 / SC-200 / SC-100).

The structure follows Microsoft's Secure Development Lifecycle (SDL) — [Design](https://learn.microsoft.com/en-us/azure/security/develop/secure-design), [Develop](https://learn.microsoft.com/en-us/azure/security/develop/secure-develop), and [Deploy](https://learn.microsoft.com/en-us/azure/security/develop/secure-deploy) — and is written to reflect **actual, independently verified state**, not aspirational targets. Where a control exists only as a plan, a framework default, or a partial mitigation, this document says so explicitly. Findings are cross-checked where possible against Azure Defender for Cloud's automated assessments (Microsoft Cloud Security Benchmark and Cloud Security Posture Management) rather than relying solely on self-assessment.

Legend used throughout: ✅ Implemented · ⚠️ Partial / in progress / inherited but unverified · ❌ Gap (not yet addressed) · — Not applicable to current scope

**Last independently verified:** Azure Defender for Cloud MCSB assessment (25.07.2026) and CSPM assessment (27.07.2026).

## Table of Contents

1. [Design Phase Security Controls](#design-phase-security-controls)
   - STRIDE Threat Model Mapping
   - Identity as the Primary Security Perimeter
   - Key Management
   - Attack Surface Reduction
   - Fail-Safe Measures, Error Handling & Logging
   - Ongoing Component Updates
2. [Implementation & Verification Phase Security Controls](#implementation--verification-phase-security-controls)
   - Implementation
   - Verification
3. [Release & Response Phase Security Controls](#release--response-phase-security-controls)
   - Release
   - Response
4. [Cross-Cutting Honest Limitations](#cross-cutting-honest-limitations)
5. [Vulnerability Disclosure](#vulnerability-disclosure)

---

## Design Phase Security Controls

This section maps our implementation against the design-phase controls recommended by Microsoft's Secure Development Lifecycle (SDL) — see [Design secure applications on Azure](https://learn.microsoft.com/en-us/azure/security/develop/secure-design). Status reflects verified state as of the last independent audit (Azure Defender for Cloud MCSB, 25.07.2026 / CSPM, 27.07.2026), not aspirational targets.

Legend: ✅ Implemented · ⚠️ Partial / needs verification · ❌ Gap (not yet addressed)

### STRIDE Threat Model Mapping

| Threat | Security Property | Azure Mitigation | Status | Notes |
|---|---|---|---|---|
| Spoofing | Authentication | Enforce HTTPS-only | ⚠️ | `https_only` previously showed as `False` in a Terraform plan diff — requires confirmation via `az webapp show --query httpsOnly` before marking resolved |
| Tampering | Integrity | TLS certificate validation | ✅ | Handled by App Service platform defaults |
| Repudiation | Non-repudiation | Monitoring & diagnostics | ✅ | Exceeds SDL baseline: Application Insights + Log Analytics + 3 active Sentinel analytics rules |
| Information Disclosure | Confidentiality | Encrypt data at rest & in transit | ⚠️ | Azure Defender MCSB flagged "Encrypt sensitive data in transit" (control DP.3) as **failed**; API returned no assessment detail, manual Portal review still pending |
| Denial of Service | Availability | DDoS protection, connection filtering | ❌ | Not implemented; not yet scheduled in backlog |
| Elevation of Privilege | Authorization | Entra ID Privileged Identity Management (PIM) | ❌ | Confirmed gap — see RBAC finding below |

### Identity as the Primary Security Perimeter

- [x] Identity-centric design from the outset (Entra External ID CIAM + Google OAuth2 + MSAL) rather than network-perimeter thinking
- [x] Managed Identity least privilege verified healthy for the App Service runtime identity (confirmed via Azure CSPM: no over-permissive role assignments)
- [ ] MFA enforcement verified for the CIAM tenant
- [ ] Legacy Authentication confirmed blocked for the CIAM tenant (Microsoft attributes ~99% of real-world password-spray success to legacy auth protocols)
- [ ] Just-in-time (JIT) access via Entra PIM — **not implemented**. Human administrative account (`147bf926-...`) holds permanent Owner at subscription scope rather than PIM-eligible, time-bound access
- [ ] Self-Service Password Reset (SSPR) — **not configured** on the Entra External ID CIAM tenant
- [ ] Passwordless authentication — **not implemented**
- [ ] Periodic Access Reviews — **not configured**
- [ ] CI/CD service principal scoped to least privilege — **confirmed gap**: `django-azure-sp` holds Contributor **and** User Access Administrator at subscription scope (should be resource-group scoped). Independently confirmed by manual RBAC review (25.07.2026) and Azure CSPM automated assessment (27.07.2026), both High severity

> **Literature backing.** An applied case study of Zero Trust Architecture on Azure — *"Analysis of Azure Zero Trust Architecture Implementation"* (Preprints.org, 2024, [doi:10.20944/preprints202407.1454.v1](https://doi.org/10.20944/preprints202407.1454.v1)) — lists JIT access, SSPR, passwordless authentication, and periodic Access Reviews alongside MFA as the standard practical components of Zero Trust identity on Azure. This project currently implements MFA and SSO but not the other four, independent of and consistent with the Azure CSPM findings below.

### Key Management

- [x] All secrets stored in Azure Key Vault (`kv-django-azure-staging`), accessed only via Private Endpoint
- [x] No secrets hardcoded in source control or environment variables — access exclusively via System-Assigned Managed Identity (`ManagedIdentityCredential()`)
- [ ] Operational hygiene around secret exposure — **gap surfaced by incident**: `DB_PASSWORD`, Django `SECRET_KEY`, and `EXTERNAL_ID_CLIENT_SECRET` were briefly printed in plaintext via `az webapp config appsettings set` run without `--output none`. Correct architecture does not by itself prevent unsafe CLI usage; secrets were rotated after discovery

### Attack Surface Reduction

- [x] MITRE ATT&CK coverage matrix maintained as a living attack-surface map (20 techniques across 9 tactics, visualized on the Security Dashboard)
- [ ] WAF / IP restrictions (ATT&CK T1595, Active Scanning) — **highest-priority open gap**. Exploitability confirmed in practice: an NMap scan against `/auth/login/` was detected by Defender for App Service on 2026-06-26 (source `20.61.126.211`)
- [ ] Formal attack surface analysis / unused-resource cleanup — not yet performed as a discrete, repeatable exercise

### Fail-Safe Measures, Error Handling & Logging

- [x] Centralized logging pipeline: OpenTelemetry → Application Insights → Log Analytics → Sentinel
- [x] User management events monitored — active Sentinel rule for repeated authentication failures (T1110, single-IP brute force)
- [ ] Distributed / low-and-slow password-spray detection — current rule only catches single-IP brute force (>10 failures); a second rule (multi-IP, low-count-per-IP spray) is planned but not yet deployed
- [ ] Explicit audit confirming credentials/tokens are never written to logs — not yet performed as a discrete checklist item

### Ongoing Component Updates

- [x] Dependency and vulnerability scanning in CI: pip-audit, Trivy, CycloneDX SBOM
- [ ] `cryptography==41.0.7` — pinned for GLIBC 2.31 compatibility on Azure App Service Linux; carries 5 known CVEs, tracked as GitHub Issue #1, unresolved due to platform constraint

---

### Honest Limitations

Consistent with CRA Annex I vulnerability-disclosure expectations, this project explicitly does **not** yet cover:

- DDoS protection or a Web Application Firewall
- A least-privilege CI/CD identity (current scope is broader than necessary)
- Just-in-time / PIM-based administrative access
- Verified encryption-in-transit status (pending manual confirmation of an automated tool finding)
- Distributed password-spray detection (only single-source brute force is currently caught)

Last independently verified against Azure Defender for Cloud MCSB (25.07.2026) and CSPM (27.07.2026) assessments.

---

## Implementation & Verification Phase Security Controls

This section maps our implementation against the code-level controls recommended by Microsoft's Secure Development Lifecycle (SDL) — see [Develop secure applications on Azure](https://learn.microsoft.com/en-us/azure/security/develop/secure-develop). Unlike the Design-phase section above, most items here concern code-level behavior rather than infrastructure — several are inherited from the Django framework by default rather than deliberately engineered, and that distinction is called out explicitly below rather than glossed over.

Legend: ✅ Implemented · ⚠️ Partial / inherited but unverified · ❌ Gap (not yet addressed) · — Not applicable to current scope

### Implementation

| Control | Status | Notes |
|---|---|---|
| Code review before merge | ❌ | No formal process documented (no CODEOWNERS, no PR-review policy enforced in the repo) |
| Static code analysis (SAST) | ✅ | Bandit runs in the 7-job CI pipeline. Note: Azure Defender MCSB flagged "Integrate SAST into DevOps" as failed — Bandit exists but isn't recognized as a native Azure DevOps integration; needs clarification (e.g. Defender for DevOps GitHub connector) |
| Input validation (allowlisting) | ⚠️ | Inherited from Django Forms/serializers by default; no explicit allowlisting strategy documented for custom views (HTMX partials, FinOps/Security endpoints) |
| Output encoding (XSS defense) | ⚠️ | Django templates auto-escape by default — this is a framework default, not a deliberate control we engineered, and should be labeled as such rather than claimed as a custom mitigation |
| Parameterized queries | ⚠️ | Django ORM is used throughout based on current architecture; not yet explicitly audited for `.raw()` or `cursor.execute()` calls that would bypass parameterization |
| Remove standard server headers (`Server`, `X-Powered-By`) | ❌ | Not checked. Action: `curl -I` against staging to confirm what's exposed |
| Segregate production data (masked dataset for dev/test) | — | No separate dev/test environment exists yet — only staging. Becomes relevant once a `production` environment is introduced (tracked separately as the environment-separation gap) |
| Strong password policy | ⚠️ | Authentication is delegated to Google OAuth2 and Entra External ID CIAM rather than custom password logic. Legacy Authentication block for the CIAM tenant is still an open TODO — relevant because ~99% of real-world password-spray attacks succeed via legacy auth per Microsoft |
| File upload validation + antimalware | — | Application does not currently accept user file uploads; explicitly noted as not applicable rather than silently omitted |
| Avoid caching sensitive content in-browser | ❌ | `Cache-Control` headers not yet checked on `/security/` and `/finops/` views, both of which render sensitive cost and alert data |

### Verification

| Control | Status | Notes |
|---|---|---|
| Dependency / SCA scanning | ✅ | pip-audit, Trivy, CycloneDX SBOM — matches the recommendation directly |
| Dynamic Application Security Testing (DAST) | ✅ | OWASP ZAP (`action-baseline`) in the 7-job pipeline. Known tooling quirks: outputs `report_json.json` not `zap_scan.sarif`; uses `allow_issue_writing`, not `allow_issue_reporting` |
| Fuzz testing | ❌ | Not implemented, not currently planned |
| Attack surface review (post-implementation) | ⚠️ | The MITRE ATT&CK coverage matrix serves a related purpose (living map of 20 techniques / 9 tactics) but is not a formal attack-surface-analyzer exercise as described in the SDL |
| Penetration testing | ❌ | No manual penetration test performed to date; automated ZAP scanning is not a substitute |
| Security Verification Tests (SVT / AzTS-equivalent) | ⚠️ | No direct AzSK/SVT equivalent, but Azure Defender for Cloud MCSB (25.07.2026) and CSPM (27.07.2026) automated assessments serve a comparable periodic-verification function at the resource level |

---

### Honest Limitations

- Several code-level protections (output escaping, ORM parameterization) are Django framework defaults, not controls we deliberately built or have explicitly verified — this document does not claim credit for framework behavior
- No formal code review process or fuzz testing exists
- No manual penetration test has been performed
- Server header disclosure and cache-control on sensitive views have not yet been checked
- File upload and dev/test data segregation controls are not applicable at current scope, not silently skipped

Last independently verified against Azure Defender for Cloud MCSB (25.07.2026) and CSPM (27.07.2026) assessments.

---

## Release & Response Phase Security Controls

This section maps our implementation against the release and response controls recommended by Microsoft's Secure Development Lifecycle (SDL) — see [Deploy secure applications on Azure](https://learn.microsoft.com/en-us/azure/security/develop/secure-deploy). Consistent with the Design and Implementation/Verification sections above, this documents actual verified state rather than aspirational targets.

Legend: ✅ Implemented · ⚠️ Partial / in progress · ❌ Gap (not yet addressed)

### Release

| Control | Status | Notes |
|---|---|---|
| Load testing before launch | ❌ | Azure Load Testing not used; application behavior under load is untested, notable given the App Service runs on the smallest available SKU (B1) |
| Web Application Firewall | ❌ | Not installed. Directly corresponds to the open ATT&CK T1595 gap (already highest priority in the backlog). Implementation path already decided: Application Gateway v2 + WAF (chosen over Front Door — single-region West Europe deployment doesn't need global edge/multi-region routing) |
| Incident response plan | ⚠️ | Initial playbooks started (`docs/playbooks/`, 25.07.2026), but no Sentinel analytics rule currently has an attached automated response (e.g. a Logic App playbook calling Microsoft Graph to revoke sessions for flagged accounts) — plan exists, isn't wired up yet |
| Final Security Review (FSR) against requirements-phase quality gates | ⚠️ | No formal pre-release FSR gate exists. Azure Defender MCSB (25.07.2026) and CSPM (27.07.2026) automated assessments serve a related function, but run post-hoc rather than as a gate before release |
| Certify release & archive | ⚠️ | Artifacts for archival exist — Terraform remote state (`stdjangotfstate35607`), SARIF reports (Bandit, Gitleaks, ZAP, Trivy) generated on every pipeline run — but there's no formal "certify release" step that consumes them as a gate |

### Response

| Control | Status | Notes |
|---|---|---|
| Execute the incident response plan | ⚠️ | Blocked on the plan above being completed and connected to alerting — nothing to execute yet beyond manual response |
| Monitor application performance | ✅ | Application Insights active with automatic anomaly detection, matching the recommendation directly |
| Microsoft Defender for Cloud | ✅ | Standard tier active. Not just configured — proven in practice: an NMap scan against `/auth/login/` was detected end-to-end (2026-06-26, source `20.61.126.211`), giving a confirmed working example rather than an untested configuration |

---

### Honest Limitations

- No load testing has been performed; behavior under real traffic (including on the B1 App Service Plan) is unverified
- No WAF is in place — the implementation path (Application Gateway v2 + WAF) is decided but not yet built
- The incident response plan exists in draft but has no automated trigger connected to any detection rule
- There is no formal pre-release security gate (FSR) — verification currently happens via periodic Azure-native assessments (MCSB, CSPM) rather than before each release
- Detection and response (Application Insights, Defender for Cloud, Sentinel) is the strongest part of this project's SDL coverage; pre-release readiness (load testing, WAF, a connected IR plan) is the acknowledged weak point, not a hidden one

Last independently verified against Azure Defender for Cloud MCSB (25.07.2026) and CSPM (27.07.2026) assessments.

---

## Cross-Cutting Honest Limitations

Pulling together the per-phase limitations above, the following are the most significant gaps in this project's security posture as of the last verification date. These are listed once here as a single reference, in addition to their phase-specific mentions:

- **No WAF / IP restrictions** — highest-priority open item (ATT&CK T1595); exploitability already confirmed via an observed NMap scan against `/auth/login/`. Implementation path decided (Application Gateway v2 + WAF), not yet built.
- **CI/CD identity is over-privileged** — the CI service principal holds Contributor and User Access Administrator at subscription scope rather than resource-group scope. Confirmed independently by manual review and Azure CSPM (High severity).
- **No PIM / just-in-time access, SSPR, passwordless authentication, or periodic Access Reviews** — the human administrative account currently holds permanent Owner at subscription scope. Confirmed independently by Azure CSPM ("Privileged roles should not have permanent access", High severity) and by the applied-Zero-Trust literature ([Analysis of Azure Zero Trust Architecture Implementation](https://doi.org/10.20944/preprints202407.1454.v1), Preprints.org 2024), which lists these four alongside MFA as standard Azure Zero Trust identity practice — this project implements MFA/SSO but not the other four.
- **No load testing** has been performed; behavior under real traffic is unverified.
- **Incident response plan is in draft** and not yet connected to any automated trigger (no Sentinel rule has an attached playbook).
- **No manual penetration test or fuzz testing** has been performed; automated DAST (ZAP) is not a substitute for either.
- **Encryption-in-transit status is unverified** — flagged by Azure Defender MCSB (control DP.3) as failed, pending manual confirmation via the Azure Portal.
- Several code-level protections (output escaping, ORM parameterization) are **Django framework defaults**, not controls this project deliberately engineered — credit is not claimed for framework behavior.

## Vulnerability Disclosure

*This section is a placeholder pending completion of the CRA Annex I vulnerability disclosure policy (VDP), tracked as an open backlog item. It is listed here as a known gap rather than left silently absent.*

When completed, this section will describe:
- How to report a security vulnerability in this project
- Expected response times
- Scope (what is and isn't covered)
- Safe harbor terms for good-faith security research

---

*This document is maintained alongside the project's security tooling (Bandit, Gitleaks, pip-audit, Trivy, CycloneDX SBOM, OWASP ZAP) and infrastructure-as-code (Terraform). It is updated as controls are implemented or as new findings emerge from Azure Defender for Cloud, Microsoft Sentinel, or manual review.*