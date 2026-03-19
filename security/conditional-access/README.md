# Conditional Access Policies

## Статус
Tenant використовує Microsoft Entra ID Free (Personal tenant).
Conditional Access потребує P1/P2 ліцензії.

Поточний захист: **Security Defaults** (активовано)

## Політики (policy-as-code для P1/P2 середовища)

### 1. policy-require-mfa.json
**Мета:** Вимагати MFA для всіх користувачів застосунку
- Застосунок: Django Falken App (773b7bfb-...)
- Виключення: Global Administrator role
- Виключення: Trusted locations
- Session frequency: 8 годин

### 2. policy-block-legacy-auth.json
**Мета:** Блокувати legacy аутентифікацію
- Охоплює: Exchange ActiveSync + інші legacy clients
- Причина: legacy auth обходить MFA

### 3. policy-require-compliant-device.json
**Мета:** Вимагати compliant device для адмінів
- Режим: Report-only (не enforced)
- Ролі: Global Admin, Security Admin
- Контролі: MFA AND compliant device

## Розгортання (з P1/P2 ліцензією)
```bash
# Створити policy через Graph API
az rest \
  --method POST \
  --uri "https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies" \
  --body @policy-require-mfa.json

# Перевірити
az rest \
  --method GET \
  --uri "https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies" \
  --query "value[].{name:displayName, state:state}" \
  -o table
```

## AZ-500 Coverage
- Domain 1: Identity (15-20%) — Conditional Access, MFA
- Named Locations, Sign-in Risk, User Risk
- Report-only mode для тестування
