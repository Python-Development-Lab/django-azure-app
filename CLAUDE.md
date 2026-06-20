# Django Azure App — Claude Code Context

## Репозиторій
- GitHub: https://github.com/Python-Development-Lab/django-azure-app
- Організація: Python-Development-Lab
- Основна гілка: main
- Робоча гілка: develop

## Архітектура
Django 6 / Python 3.12 на Azure App Service (Linux, Standard S1)
Автентифікація: Microsoft Entra ID OAuth2 + MSAL
Секрети: Azure Key Vault + System-Assigned Managed Identity
База даних: PostgreSQL Flexible Server 16 (Standard_B1ms)
Моніторинг: OpenTelemetry → Application Insights → Log Analytics → Sentinel
Мережа: VNet + NSG + Private Endpoints (Key Vault + PostgreSQL)
CI/CD: GitHub Actions (ci.yml, deploy-staging.yml, deploy-production.yml)

## Ключові патерни
- BUILDING=true: пропускає Key Vault під час Oryx build (collectstatic)
- Managed Identity: ніяких credentials в коді або env змінних
- Slot swap: zero-downtime deployment через staging slot
- terraform destroy/apply: повне розгортання/знищення інфраструктури

## Структура
auth_app/          — Entra ID backend, MSAL, RBAC декоратори, middleware
core/              — основні views
djangoapp/         — settings, key_vault, monitoring, wsgi
security/          — policy-as-code (WAF, PIM, Conditional Access)
terraform/         — IaC модулі (network, key_vault, database, app_service, monitoring)
scripts/           — deploy.sh, destroy.sh
.devcontainer/     — GitHub Codespaces конфігурація

## Terraform
Розгортання: cd terraform && terraform init && terraform plan
Знищення: bash scripts/destroy.sh
State: локальний (треба додати Azure Blob backend для team use)

## AZ-500 Coverage ~90%
Domain 1: Entra ID, MSAL, RBAC, PIM (policy-as-code)
Domain 2: VNet, NSG, Private Endpoints, WAF
Domain 3: App Service, PostgreSQL, Key Vault, Storage
Domain 4: Sentinel, Defender for Cloud, Application Insights

## Сертифікаційний roadmap
SC-200 → наступний (Sentinel, Defender вже є)
AZ-305 → ADR документи в docs/adr/
AZ-400 → Trivy scanning, SBOM в CI pipeline

## Заборонено
- Ніяких секретів в коді або git
- Ніяких credentials в environment variables (тільки Key Vault)
- terraform.tfvars не комітити (.gitignore)
