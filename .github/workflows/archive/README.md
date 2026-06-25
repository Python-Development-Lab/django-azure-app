# Archived Workflows

These workflows are kept for historical reference only.
They were used before the migration to the full DevSecOps pipeline.

## Why archived

| File | Reason |
|------|--------|
| `ci.yml` | Replaced by Tests & Lint job in `deploy-staging-terraform.yml` |
| `deploy-staging.yml` | Old app `mydjango1772289446`, no Terraform, no security scanning |
| `deploy-production.yml` | Old app, Python 3.10, no security scanning |
| `deploy.yml` | Oldest version, basic deploy only |

## Current active workflows

- `../deploy-staging-terraform.yml` — 7-job DevSecOps pipeline (Security Scan, IaC Scan, Tests, Terraform, Deploy, DAST)
- `../destroy-staging.yml` — Manual destroy with audit trail
