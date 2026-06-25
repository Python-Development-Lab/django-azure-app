# Conditional Access Policies — Policy as Code

Ці policies реалізують Zero Trust Device Health Verification
відповідно до NIST SP 800-207 принципу 7.

## Статус

| Policy | Файл | Ліцензія | Статус |
|--------|------|----------|--------|
| Block Legacy Auth | policy-block-legacy-auth.json | Free | ✅ Активна |
| Require MFA | policy-require-mfa.json | P1 | 📋 Policy-as-Code |
| Require Compliant Device | policy-require-compliant-device.json | P1 | 📋 Policy-as-Code |

## Вимоги для активації

Для активації `compliantDevice` control потрібна:
- Azure AD Premium P1 ліцензія (~€6/user/month)
- Microsoft Intune для device enrollment
- Мінімум 1 enrolled пристрій

## Застосування через Graph API

```bash
TOKEN=$(az account get-access-token \
  --resource https://graph.microsoft.com \
  --query accessToken -o tsv)

curl -X POST \
  "https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @policy-require-compliant-device.json
```

## Django-рівень Device Verification

Реалізовано в `auth_app/middleware.py` через `DeviceVerificationMiddleware`:
- User-Agent fingerprinting
- IP geolocation anomaly detection
- Session consistency checks
- Suspicious device alerts → Sentinel

## Zero Trust Coverage

Цей модуль закриває NIST SP 800-207 принцип 7:
"Device health is verified before granting access"

AZ-500 Domain 1: Identity and Access Management
SC-100: Zero Trust Architecture
