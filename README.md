# Django Azure Security Template

> Production-ready Django application template with **Security by Design**, Azure cloud infrastructure, and automated CI/CD pipelines. Built and validated through a full AZ-500 security sprint covering all four exam domains.

---

## Overview

This template provides a secure, production-grade foundation for Django applications deployed to Azure App Service. Instead of adding security as an afterthought, every component is designed with security as a first principle — from identity and networking to monitoring and governance.

**What you get out of the box:**

- Microsoft Entra ID (Azure AD) authentication via OAuth2 + MSAL
- Secrets management via Azure Key Vault with Managed Identity (no passwords in code)
- PostgreSQL Flexible Server with audit logging
- Full observability stack (OpenTelemetry → Application Insights → Log Analytics)
- Private networking (VNet, NSG, Private Endpoints)
- Zero-downtime deployments via staging slots
- Microsoft Defender for Cloud + Microsoft Sentinel
- Azure Policy enforcement
- Automated CI/CD with GitHub Actions

---

## Security by Design Principles

| Principle | Implementation |
|---|---|
| Minimize Attack Surface | Private Endpoints, NSG deny-all, Storage firewall |
| Least Privilege | Managed Identity with Key Vault Secrets User role only |
| Defense in Depth | 6 independent security layers |
| Secure Defaults | TLS 1.2+, HTTPS only, Azure Policy enforcement |
| Audit Everything | OpenTelemetry, pgaudit, KV audit logs, Sentinel |
| Fail Securely | BUILDING flag skips KV during Oryx build |
| Separation of Duties | Production + staging environments, separate Managed Identities |

---

## Architecture

```
Internet
    ↓ HTTPS 443
Azure App Service (Production + Staging slot)
    ↓ Microsoft Entra ID OAuth2
    ↓ VNet Integration
app-subnet (10.0.1.0/24) ← NSG: Allow 443, Deny All
    ↓
data-subnet (10.0.2.0/24)
    ├── 10.0.2.4 → Azure Key Vault  (Private Endpoint)
    └── 10.0.2.5 → PostgreSQL       (Private Endpoint)

Monitoring:
App Service → OpenTelemetry → Application Insights → Log Analytics
                                                           ↓
                                                   Microsoft Sentinel
                                                   (Analytics Rules)
```

---

## Prerequisites

Before deploying, you need:

- Azure subscription with Owner or Contributor access
- Microsoft Entra ID tenant (free tier works for basic auth)
- GitHub account with Actions enabled
- Azure CLI installed locally or GitHub Codespaces
- Python 3.12+

---

## Quick Start

### Step 1 — Create a new repository from this template

Click **Use this template** → **Create a new repository** on GitHub. Choose a name and visibility for your project.

### Step 2 — Clone your new repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_PROJECT_NAME
cd YOUR_PROJECT_NAME
```

### Step 3 — Create Azure infrastructure

```bash
# Login to Azure
az login --tenant "YOUR_TENANT_ID"

# Create resource group
az group create \
  --name "your-app-rg" \
  --location "westeurope"

# Create App Service Plan (Standard S1 required for deployment slots)
az appservice plan create \
  --name "your-app-plan" \
  --resource-group "your-app-rg" \
  --sku S1 \
  --is-linux

# Create App Service
az webapp create \
  --name "your-app-name" \
  --resource-group "your-app-rg" \
  --plan "your-app-plan" \
  --runtime "PYTHON:3.12"

# Create Key Vault
az keyvault create \
  --name "your-app-kv" \
  --resource-group "your-app-rg" \
  --enable-rbac-authorization true

# Create PostgreSQL
az postgres flexible-server create \
  --name "your-app-db" \
  --resource-group "your-app-rg" \
  --sku-name "Standard_B1ms" \
  --version "16"
```

### Step 4 — Configure Microsoft Entra ID App Registration

```bash
# Create App Registration
az ad app create \
  --display-name "Your App Name" \
  --web-redirect-uris "https://your-app-name.azurewebsites.net/auth/callback/"

# Note the appId — you will need it for Key Vault secrets
```

### Step 5 — Store secrets in Key Vault

```bash
KV_NAME="your-app-kv"

# Django secret key
az keyvault secret set --vault-name $KV_NAME \
  --name "DJANGO-SECRET-KEY" \
  --value "$(python3 -c "import secrets,string; print(''.join(secrets.choice(string.ascii_letters+string.digits+'-_') for _ in range(64)))")"

# Entra ID credentials
az keyvault secret set --vault-name $KV_NAME \
  --name "AZURE-CLIENT-ID" --value "your-entra-app-client-id"

az keyvault secret set --vault-name $KV_NAME \
  --name "AZURE-CLIENT-SECRET" --value "your-entra-app-client-secret"

az keyvault secret set --vault-name $KV_NAME \
  --name "AZURE-TENANT-ID" --value "your-tenant-id"

# Database credentials
az keyvault secret set --vault-name $KV_NAME \
  --name "DB-HOST" --value "your-app-db.postgres.database.azure.com"

az keyvault secret set --vault-name $KV_NAME \
  --name "DB-NAME" --value "djangodb"

az keyvault secret set --vault-name $KV_NAME \
  --name "DB-USER" --value "your-db-admin"

az keyvault secret set --vault-name $KV_NAME \
  --name "DB-PASSWORD" --value "your-db-password"
```

### Step 6 — Enable Managed Identity and grant Key Vault access

```bash
# Enable system-assigned managed identity
az webapp identity assign \
  --name "your-app-name" \
  --resource-group "your-app-rg"

# Get the principal ID
PRINCIPAL_ID=$(az webapp identity show \
  --name "your-app-name" \
  --resource-group "your-app-rg" \
  --query "principalId" -o tsv)

KV_ID=$(az keyvault show \
  --name "your-app-kv" \
  --resource-group "your-app-rg" \
  --query "id" -o tsv)

# Grant Key Vault Secrets User role
az role assignment create \
  --role "Key Vault Secrets User" \
  --assignee "$PRINCIPAL_ID" \
  --scope "$KV_ID"
```

### Step 7 — Configure App Service settings

```bash
az webapp config appsettings set \
  --name "your-app-name" \
  --resource-group "your-app-rg" \
  --settings \
    "AZURE_KEY_VAULT_NAME=your-app-kv" \
    "AZURE_TENANT_ID=your-tenant-id" \
    "ALLOWED_HOSTS=your-app-name.azurewebsites.net" \
    "AZURE_REDIRECT_URI=https://your-app-name.azurewebsites.net/auth/callback/" \
    "OTEL_SERVICE_NAME=your-app-name-production" \
    "BUILDING=true" \
    "DEBUG=False"
```

### Step 8 — Configure GitHub Secrets

In your repository go to **Settings → Secrets and variables → Actions** and add:

| Secret | Value |
|---|---|
| `AZURE_CREDENTIALS` | JSON output of `az ad sp create-for-rbac` |
| `AZURE_APP_NAME` | your-app-name |
| `AZURE_RESOURCE_GROUP` | your-app-rg |

```bash
# Generate AZURE_CREDENTIALS
az ad sp create-for-rbac \
  --name "github-actions-your-app" \
  --role "Contributor" \
  --scopes "/subscriptions/YOUR_SUBSCRIPTION_ID/resourceGroups/your-app-rg" \
  --sdk-auth
```

### Step 9 — Deploy

Push to `main` branch — GitHub Actions will automatically build and deploy:

```bash
git push origin main
```

---

## Project Structure

```
├── .azure/                         # Azure configuration
├── .github/
│   ├── pull_request_template.md    # PR template with security checklist
│   └── workflows/
│       ├── ci.yml                  # Lint + tests on every PR
│       ├── deploy-production.yml   # main → production deployment
│       └── deploy-staging.yml      # develop → staging deployment
├── auth_app/
│   ├── backends.py                 # Custom EntraID authentication backend
│   ├── decorators.py               # RBAC decorators (@require_role)
│   ├── middleware.py               # Token refresh middleware
│   ├── msal_service.py             # MSAL OAuth2 service
│   ├── views.py                    # Login, callback, logout views
│   └── urls.py
├── core/
│   ├── views.py                    # Application views (home, dashboard)
│   └── urls.py
├── djangoapp/
│   ├── key_vault.py                # Key Vault secret loader
│   ├── monitoring.py               # OpenTelemetry configuration
│   ├── settings.py                 # Django settings with BUILDING flag
│   └── wsgi.py
├── security/
│   ├── conditional-access/         # Conditional Access policies (policy-as-code)
│   ├── pim/                        # PIM role settings (policy-as-code)
│   └── waf/                        # WAF + Application Gateway config (policy-as-code)
├── templates/
│   ├── auth/                       # Login and error pages
│   ├── base/                       # Base HTML template
│   └── core/                       # Application pages
├── .env.example                    # Environment variables template
├── manage.py
├── pytest.ini
├── requirements.txt
└── startup.sh                      # Azure App Service startup script
```

---

## CI/CD Pipeline

```
Push to develop → CI (lint + tests) → Deploy to Staging
                                            ↓
                                   Manual verification
                                            ↓
Push to main   → CI (lint + tests) → Deploy to Production
                                   (zero-downtime via slot swap)
```

The pipeline uses `azure/login` with `AZURE_CREDENTIALS` (service principal) — not publish profiles, which are less secure and unreliable for slot deployments.

---

## Key Components Explained

### Key Vault Integration (`djangoapp/key_vault.py`)

Secrets are loaded from Azure Key Vault at application startup using the App Service Managed Identity. No passwords are stored in environment variables or configuration files.

The `BUILDING=true` flag prevents Key Vault loading during the Oryx build process (where Managed Identity is unavailable), allowing `collectstatic` to run cleanly.

### Authentication Flow

```
User visits app → Redirect to Microsoft login
                        ↓
            Microsoft Entra ID OAuth2
                        ↓
            Callback with authorization code
                        ↓
            MSAL exchanges code for tokens
                        ↓
            Custom backend creates/updates Django user
                        ↓
            Session established → App access
```

### Monitoring (`djangoapp/monitoring.py`)

OpenTelemetry automatically instruments Django, PostgreSQL queries, and HTTP calls. All telemetry flows to Application Insights and is queryable via KQL in Log Analytics:

```kql
// Recent requests
AppRequests
| where TimeGenerated > ago(1h)
| summarize count() by Name

// Failed requests
AppRequests
| where Success == false
| project TimeGenerated, Name, ResultCode
```

### Security Policy-as-Code (`security/`)

The `security/` directory contains policy definitions that can be deployed when the appropriate Azure tier is available:

- `conditional-access/` — MFA enforcement, legacy auth blocking, compliant device policies (requires Entra ID P1/P2)
- `pim/` — Just-In-Time role activation settings (requires Entra ID P2)
- `waf/` — Application Gateway WAF with OWASP 3.2, bot protection, geo-blocking

---

## Customisation Checklist

When using this template for a new project, update the following:

```
Settings:
[ ] djangoapp/settings.py — update OTEL_SERVICE_NAME, ALLOWED_HOSTS
[ ] .github/workflows/*.yml — update app-name, resource-group
[ ] Copy .env.example to .env for local development

New Azure Resources per project:
[ ] App Service + Plan
[ ] Key Vault (recommended: one per application)
[ ] PostgreSQL database (can share server, use separate DB)
[ ] Entra ID App Registration (one per application)
[ ] Managed Identity + RBAC assignments

GitHub Secrets:
[ ] AZURE_CREDENTIALS
[ ] AZURE_APP_NAME
[ ] AZURE_RESOURCE_GROUP
```

---

## Cost Estimate (westeurope region)

| Resource | SKU | Monthly cost |
|---|---|---|
| App Service Plan S1 | Standard (required for slots) | ~€56 |
| PostgreSQL Flexible Server | Standard_B1ms | ~€13 |
| Azure Key Vault | Standard (10K ops) | ~€0.30 |
| Azure Storage Account | Standard LRS | ~€0.50 |
| Private Endpoints (×2) | VNet integration | ~€14 |
| Log Analytics | PerGB2018 (< 5GB free) | ~€0 |
| **Total** | | **~€85/month** |

When sharing the App Service Plan and PostgreSQL server across multiple applications, each additional app costs approximately €25–30/month.

---

## AZ-500 Coverage

This template was built as a practical study project for the Microsoft AZ-500 Security Engineer certification and covers approximately 90% of exam domains through hands-on implementation:

| Domain | Coverage |
|---|---|
| Domain 1 — Identity and Access | ~80% |
| Domain 2 — Secure Networking | ~100% |
| Domain 3 — Compute, Storage, Databases | ~85% |
| Domain 4 — Defender for Cloud + Sentinel | ~90% |

---

## Contributing

Pull requests are welcome. For major changes, open an issue first to discuss what you would like to change. Please ensure all security-related changes follow the existing Security by Design principles documented in the `security/` directory.

---

## License

MIT — free to use, modify, and distribute.

---

