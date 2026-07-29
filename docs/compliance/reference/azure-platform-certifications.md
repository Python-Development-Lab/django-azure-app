# Azure Platform Certifications — Shared Responsibility Mapping

**Project:** django-azure-app
**Purpose:** Document which security/compliance assurances are inherited from the underlying Microsoft Azure platform (via Microsoft's own third-party audits) versus which are the responsibility of this application/infrastructure layer.
**Last reviewed:** 27.07.2026

---

## 1. Source Documents Reviewed

| Certification | Standard | Scope Owner | Issue Date (reviewed copy) | Expiration (reviewed copy) | Status as of 27.07.2026 |
|---|---|---|---|---|---|
| ISO/IEC 20000-1:2018 Recertification Summary Report | Service Management System (SMS) | Microsoft Corporation | 24.04.2023 | Report itself has no expiry; next full recertification cycle scheduled 2026 per the certificate's own cycle table | ⚠️ Needs refresh — 2026 recertification cycle is due/in progress |
| ISO/IEC 27017:2015 Certificate (No. 1411732-9, v9) | Cloud-specific information security controls | Microsoft Corporation | 18.05.2023 | **13.06.2026** | 🔴 Expired — pull current certificate from Microsoft Service Trust Portal |
| ISO/IEC 27018:2019 Certificate (No. 1186580-10, v10) | Protection of PII in public clouds | Microsoft Corporation | 18.05.2023 | **18.12.2025** | 🔴 Expired — pull current certificate from Microsoft Service Trust Portal |

**Action item:** Before citing these in `SECURITY.md` or any CompliGuard/NIS2 materials, replace with current copies downloaded directly from Microsoft's [Service Trust Portal](https://servicetrust.microsoft.com) or [Trust Center](https://www.microsoft.com/trust-center) — the certificates in hand are stale by 1–2 years and Microsoft is virtually certain to have renewed by now, but the specific document (version number, exact expiry date) needs to reflect the live one for any audit-facing claim.

---

## 2. What These Certifications Actually Cover

All three documents share the **same scope boundary**, explicitly stated in each:

> "...the SMS/ISMS supporting **Microsoft Azure, Dynamics 365, and other Online Services** that are deployed in Azure Public and Government Cloud including their **development, operations, and infrastructure**..."

Concretely, this means Microsoft's audited scope is:

- Physical datacenter security (the ~150 locations listed across the Appendix — Amsterdam, Frankfurt, Dublin, etc.)
- The Azure control plane services themselves (App Service, Key Vault, PostgreSQL Flexible Server, VNet, Sentinel, Defender for Cloud, etc. — as *platform offerings*)
- Microsoft's internal SDLC, change management, incident response, and supplier management processes for building and operating those platform services
- ISO 27017: cloud-specific controls (e.g., shared responsibility clarity, virtual machine hardening guidance Microsoft itself follows, tenant isolation)
- ISO 27018: how Microsoft as a cloud provider handles PII in the services it operates (e.g., not using customer data for advertising, breach notification commitments, data location controls)

**This is a "security of the cloud" scope, not a "security in the cloud" scope** — the standard AWS/Azure/GCP shared responsibility split.

---

## 3. Shared Responsibility Mapping for django-azure-app

| Layer | Covered by Microsoft's ISO 20000-1 / 27017 / 27018? | Responsibility of this project |
|---|---|---|
| Physical datacenter security, hardware lifecycle | ✅ Yes | N/A |
| Hypervisor / host OS isolation between tenants | ✅ Yes (ISO 27017 tenant isolation controls) | N/A |
| Azure service availability & platform incident response | ✅ Yes (ISO 20000-1 SMS) | N/A |
| Encryption at rest offered by Azure Storage/PostgreSQL/Key Vault | ✅ Platform capability exists and is audited | Project must **enable and configure** it correctly (e.g., confirm PostgreSQL Flexible Server storage encryption, Key Vault soft-delete/purge protection) |
| Azure IAM/RBAC engine (Entra ID) as a *mechanism* | ✅ Yes (ISO 27017/27018 identity controls) | Project owns **how RBAC is actually assigned** — this is exactly where the known over-privilege findings live (django-azure-sp holding subscription-scope Contributor + User Access Administrator; human admin holding subscription-scope Owner without PIM) |
| Network isolation primitives (VNet, NSG, Private Endpoint) | ✅ Platform primitives audited | Project owns **NSG rule design, subnet segmentation, Private Endpoint usage** — this is where the T1595/WAF gap and the NAT Gateway/outbound-IP analysis live |
| PII handling *by Microsoft* (e.g., not scanning customer content for ads) | ✅ ISO 27018 | Project owns **PII handling in application code** — Django models, logging (make sure `AppServiceHTTPLogs`/Sentinel queries don't leak PII into KQL results retained long-term), CIAM user data flows |
| Logging/monitoring *infrastructure* (Log Analytics, Sentinel, Defender for Cloud as products) | ✅ Platform audited | Project owns **what gets logged, retention, and whether diagnostic settings are actually turned on** — directly relevant to the 24.07.2026 Key Vault/PostgreSQL diagnostic-settings gap that was found and closed |
| Application code security (Django views, middleware, auth flows) | ❌ Not in scope of these certs at all | 100% project responsibility — Bandit/Gitleaks/pip-audit/Trivy/ZAP pipeline, DeviceVerificationMiddleware, KBSSE-aspirational threat ontology |
| Terraform/IaC correctness | ❌ Not in scope | 100% project responsibility |
| CI/CD pipeline secret hygiene (AZURE_CREDENTIALS, exposed secrets incident) | ❌ Not in scope | 100% project responsibility |
| Least-privilege DB role (`azuresu` vs `django_app_user`) | ❌ Not in scope | 100% project responsibility |

---

## 4. Relevance to Open Backlog Items

- **MCSB cross-reference doc (`docs/compliance/mcsb-cross-reference.md`, planned):** for controls like *"Encrypt sensitive data in transit"* or *"Enable logging for security investigation,"* note explicitly which portion is inherited from the Azure platform's own ISO 27017/27018 posture versus which portion depends on this project's own configuration (diagnostic settings, TLS enforcement on App Service, `https_only` setting). Avoid double-counting: Microsoft being ISO-certified does not mean *this app's* `https_only` misconfiguration finding is resolved.
- **SECURITY.md "Honest Limitations" section (planned):** a short paragraph citing that the underlying Azure platform holds ISO 20000-1 / 27017 / 27018 / 27001 / 22301 / 9001 and CSA STAR is legitimate and strengthens the document, provided it's paired with an explicit statement that these certifications do not extend to this project's application code, IaC, or CI/CD practices — which is the real content of the "Honest Limitations" section.
- **CompliGuard / NIS2 (future, post-fork):** the datacenter list confirms EU-region options (West Europe/Amsterdam, Germany West Central/Frankfurt, Germany North/Berlin, France Central/Paris, Sweden Central) are within Microsoft's ISO 27017/27018 scope — useful groundwork for a future NIS2 data-residency argument, but NIS2 compliance itself will still depend entirely on CompliGuard's own application-layer controls, not on Microsoft's certificates.

---

## 5. Recommended Next Steps

1. Download current, non-expired versions of ISO 27017 and ISO 27018 certificates from the Microsoft Service Trust Portal before citing dates/expiry in any external-facing document.
2. When drafting `SECURITY.md`, use the mapping table in Section 3 as the basis for the "Honest Limitations" framing — cite what's inherited vs. owned, rather than listing Microsoft's certifications as if they were this project's own.
3. Cross-reference this file from `docs/compliance/mcsb-cross-reference.md` once that document is created, to avoid restating the shared-responsibility argument twice.
