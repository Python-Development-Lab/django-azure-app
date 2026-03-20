# WAF + Application Gateway

## Статус
Application Gateway WAF_v2 задокументовано як Infrastructure-as-Code.
Не розгорнуто через вартість (~€250/міс для WAF_v2).
Для production середовища рекомендується розгортання через Bicep шаблон.

## Архітектура з WAF
```
Internet
    ↓ HTTPS 443
Azure Application Gateway (WAF_v2)
    ↓ WAF inspection
    ├── OWASP 3.2 ruleset
    ├── Bot Manager ruleset
    ├── Custom rules (rate limit, geo-block)
    ↓
App Service (mydjango1772289446)
    ↓ VNet Integration
data-subnet
    ├── Key Vault  (10.0.2.4)
    └── PostgreSQL (10.0.2.5)
```

## WAF Policy — захист

### OWASP 3.2 (автоматично блокує)
- SQL Injection (SQLi)
- Cross-Site Scripting (XSS)
- Local/Remote File Inclusion (LFI/RFI)
- Remote Code Execution (RCE)
- HTTP Protocol Violations
- Scanner Detection

### Custom Rules
- BlockSuspiciousUserAgents — блокує sqlmap, nikto, nmap, masscan
- RateLimitLogin — max 20 запитів/хв на /auth/login та /auth/callback
- AllowOnlyUkraineAndEU — гео-блокування (UA, DE, PL, NL, FR, GB, SE, FI)

### HTTP → HTTPS redirect
- Порт 80 автоматично редіректить на 443
- TLS 1.2 minimum

## Розгортання (Bicep)
```bash
# Потрібна додаткова subnet для App Gateway
az network vnet subnet create \
  --name "appgw-subnet" \
  --resource-group "my-django-rg" \
  --vnet-name "django-vnet" \
  --address-prefix "10.0.3.0/24"

# Public IP для App Gateway
az network public-ip create \
  --name "django-appgw-pip" \
  --resource-group "my-django-rg" \
  --sku Standard \
  --allocation-method Static

# App Gateway з WAF (увага: ~€250/міс)
az network application-gateway create \
  --name "django-appgw" \
  --resource-group "my-django-rg" \
  --sku WAF_v2 \
  --capacity 1 \
  --vnet-name "django-vnet" \
  --subnet "appgw-subnet" \
  --public-ip-address "django-appgw-pip" \
  --http-settings-protocol Https \
  --http-settings-port 443 \
  --servers "mydjango1772289446.azurewebsites.net" \
  --waf-policy "django-waf-policy"
```

## Альтернатива — Azure Front Door + WAF (~€20-30/міс)
```bash
az afd profile create \
  --profile-name "django-frontdoor" \
  --resource-group "my-django-rg" \
  --sku Standard_AzureFrontDoor

az afd waf-policy create \
  --policy-name "django-waf-policy" \
  --resource-group "my-django-rg" \
  --sku Standard_AzureFrontDoor \
  --mode Prevention
```

## AZ-500 Coverage
- Domain 2: Secure Networking (20-25%)
- WAF policies, OWASP ruleset, custom rules
- Application Gateway health probes
- TLS termination, HTTP→HTTPS redirect
- DDoS protection integration
