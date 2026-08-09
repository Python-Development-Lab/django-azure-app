# Repo conventions

This file is intentionally short. Update it only when an architectural invariant actually changes.

## Non-negotiable invariants

- Secrets: Key Vault only, via System-Assigned Managed Identity. No secrets in app settings, no secrets printed to CI logs.
- BUILDING=true pattern: Key Vault is unreachable during the Oryx build phase.
- Multi-tenancy is out of scope: this repo is single-tenant. Do not introduce Tenant models or tenant middleware here.
- RBAC scope: prefer resource-group scope over subscription scope for new role assignments.
- Terraform module boundaries: currently 7 modules (network, key_vault, database, app_service, monitoring, sarif_archive, cost_export -- see docs/adr/0003-seventh-terraform-module.md). New modules for genuinely separate concerns are acceptable; avoid a module per single resource.
- HTMX endpoints: bundle rate-limited API calls into a single endpoint.

## Known accepted risks

- cryptography==41.0.7 pinned: cryptography>=42.0.0 uses Rust bindings incompatible with GLIBC 2.31 on Azure App Service (Debian 11 Bullseye), tracked in GitHub Issue #1.
- EXTERNAL_ID_* app settings show as null in terraform apply diffs, expected.

## Where to look harder

- Diffs touching key_vault or database modules, or IAM role assignments.
- Diffs touching startup.sh or app settings ordering.