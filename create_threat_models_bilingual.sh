#!/usr/bin/env bash
set -e

echo "=== Крок 1: docs/threat-models/TEMPLATE.md (українська) ==="
mkdir -p docs/threat-models

cat > docs/threat-models/TEMPLATE.md << 'EOF'
# Threat Model Template (STRIDE)

> Заповнювати ДО імплементації фічі, не після — узгоджено з принципом
> Spec-Driven Development (специфікація/аналіз перед кодом).

---
feature: <назва фічі>
date: <YYYY-MM-DD>
status: draft
---

## Компонент і межі довіри (trust boundaries)

<Опишіть компонент і всі межі довіри, які він перетинає — наприклад,
"браузер користувача → Django view → зовнішній API → база даних".
Кожна межа — потенційна точка атаки.>

## STRIDE-аналіз

### Spoofing (видача себе за іншого)
<Чи може хтось видати себе за легітимного користувача/сервіс/дані?>

### Tampering (несанкціонована зміна)
<Чи може хтось змінити дані/код/конфігурацію без дозволу?>

### Repudiation (заперечення дії)
<Чи може хтось заперечити свою дію без достатніх доказів/логів?>

### Information Disclosure (витік інформації)
<Чи може конфіденційна інформація потрапити не тим адресатам?>

### Denial of Service (відмова в обслуговуванні)
<Чи може хтось зробити компонент/систему недоступною?>

### Elevation of Privilege (підвищення привілеїв)
<Яку роль/MSI/права матиме цей компонент? Чи є ризик отримати вищі
права, ніж передбачено?>

## Виявлені пункти дій

- [ ] <Дія 1> → пов'язана MITRE ATT&CK техніка (якщо релевантно): T____
- [ ] <Дія 2>

## Пов'язані записи

- ADR: <посилання на docs/adr/*.md, якщо є>
- Compliance: <посилання на docs/compliance/*.md, якщо є>
- Playbook: <посилання на docs/playbooks/*.md, якщо є>
EOF

echo "OK: TEMPLATE.md створено"

echo ""
echo "=== Крок 2: docs/threat-models/TEMPLATE.en.md (English) ==="

cat > docs/threat-models/TEMPLATE.en.md << 'EOF'
# Threat Model Template (STRIDE)

> Fill in BEFORE implementing the feature, not after — aligned with the
> Spec-Driven Development principle (specification/analysis before code).

---
feature: <feature name>
date: <YYYY-MM-DD>
status: draft
---

## Component and Trust Boundaries

<Describe the component and every trust boundary it crosses — e.g.
"user's browser → Django view → external API → database". Each
boundary is a potential attack point.>

## STRIDE Analysis

### Spoofing
<Can someone impersonate a legitimate user/service/data source?>

### Tampering
<Can someone modify data/code/configuration without authorization?>

### Repudiation
<Can someone deny an action without sufficient evidence/logs?>

### Information Disclosure
<Can confidential information reach unintended recipients?>

### Denial of Service
<Can someone make the component/system unavailable?>

### Elevation of Privilege
<What role/MSI/permissions will this component have? Is there a risk
of obtaining higher privileges than intended?>

## Identified Action Items

- [ ] <Action 1> → related MITRE ATT&CK technique (if relevant): T____
- [ ] <Action 2>

## Related Records

- ADR: <link to docs/adr/*.md, if any>
- Compliance: <link to docs/compliance/*.md, if any>
- Playbook: <link to docs/playbooks/*.md, if any>
EOF

echo "OK: TEMPLATE.en.md created"

echo ""
echo "=== Крок 3: docs/threat-models/0001-ask-ai-alert-panel.md (українська) ==="

cat > docs/threat-models/0001-ask-ai-alert-panel.md << 'EOF'
# Threat Model: Ask AI About This Alert Panel

---
feature: Ask AI about this alert panel
date: 2026-07-25
status: draft
---

## Компонент і межі довіри (trust boundaries)

Планована фіча: користувач натискає на алерт (Sentinel/Defender/ATT&CK
coverage gap) у Security Dashboard → Django view збирає JSON-контекст
(coverage matrix, alert details, HTTP anomalies) → передає в Claude API →
відповідь (пояснення + suggested Terraform fix) → рендериться користувачу
в браузері.

Межі довіри, що перетинаються:
1. Браузер користувача → Django view (стандартна, вже покрита MSAL/CIAM auth)
2. Django view → зовнішній Claude API (НОВА межа, дані покидають Azure-периметр)
3. Відповідь Claude API → рендеринг у браузері (потенційна XSS-поверхня,
   якщо відповідь містить неекранований HTML/markdown)
4. Suggested Terraform fix → потенційне подальше застосування людиною
   (НЕ automated apply — критична межа, яку слід тримати ручною)

## STRIDE-аналіз

### Spoofing
Хтось може підробити параметр alert_id у запиті до view, змусивши
систему зібрати й відправити в Claude API контекст ЧУЖОГО алерту/іншого
tenant-simulated даних. Мітигація: перевіряти, що alert_id належить до
поточної автентифікованої сесії/workspace, не приймати довільний ID
без валідації проти реального Sentinel workspace.

### Tampering
Якщо JSON-контекст формується з кількох джерел (coverage matrix +
live Sentinel alert + HTTP anomalies), хтось із проміжним доступом до
мережі/логів теоретично міг би підмінити дані до того, як вони потраплять
у промпт. Мітигація: увесь збір відбувається server-side через уже
автентифіковані MSI-виклики (Log Analytics), без proxy через клієнта.

### Repudiation
Немає audit trail того, які саме suggested fixes AI-панель колись
згенерувала і чи хтось їх застосував. Це прямий, ще не закритий gap —
MUST HAVE перед релізом: логувати кожен запит (хто, коли, який alert_id,
яка відповідь) в окрему таблицю/AppTraces запис.

### Information Disclosure — НАЙКРИТИЧНІШИЙ РОЗДІЛ
- Дані Sentinel-алертів (можливо, включно з реальними IP, User-Agent,
  іменами користувачів) покидають Azure-периметр і йдуть у зовнішній
  Claude API. Це вимагає explicit рішення: чи прийнятно передавати ці
  дані назовні, чи потрібна попередня анонімізація/редакція PII.
- Ризик, що структурований контекст (Terraform resource names, subnet
  ranges, subscription ID) стає частиною запиту до стороннього сервісу.
  Мітигація: мінімізувати контекст до необхідного мінімуму; НЕ включати
  сирі секрети чи повні Terraform-файли, тільки резюмовані факти
  (technique_id, status, короткий control/detection текст).
- Knowledge leakage в іншому напрямку: AI може "здогадатись" деталі
  архітектури з тренувальних даних і представити здогадку як факт про
  ЦЮ систему — вимагає explicit трасування claim → конкретне поле
  вхідного JSON.

### Denial of Service
Немає rate limiting на новий ендпоінт — теоретично хтось із доступом до
Security Dashboard міг би спамити запитами до Claude API, спричиняючи
непередбачувані витрати/затримки. Мітигація: rate limit на рівні view
(наприклад, django-ratelimit) + короткий TTL-кеш для однакових alert_id.

### Elevation of Privilege
Найкритичніша вимога: MSI/service, що виконує цей виклик, повинен мати
СТРОГО read-only доступ до Log Analytics/Sentinel API. Suggested
Terraform fix НІКОЛИ не повинен автоматично застосовуватись (`terraform
apply`) без явної, окремої, ручної дії людини — Claude API тут генерує
тільки ТЕКСТ рекомендації, не виконує жодних змін інфраструктури.
Верифікаційний крок (чи згадані в рекомендації Terraform-ресурси реально
існують у поточному стейті) повинен виконуватись ДО показу відповіді
користувачу, не після.

## Виявлені пункти дій

- [ ] Валідація alert_id проти реального workspace перед збором контексту
- [ ] Audit-логування кожного AI-запиту (хто/коли/що) → пов'язано з A.8.15 Logging
- [ ] Explicit рішення щодо PII-редакції в контексті перед відправкою в Claude API
- [ ] Rate limiting на ендпоінт
- [ ] Верифікація згаданих Terraform-ресурсів проти реального стейту перед показом рекомендації
- [ ] Explicit MSI-роль: тільки read (Log Analytics Reader, Security Reader) — НІКОЛИ write/Contributor
- [ ] Явне цитування джерела кожного твердження (яке поле JSON) у відповіді AI

## Пов'язані записи

- Compliance: A.8.15/A.8.16 Logging & Monitoring (docs/compliance/0015, 0016)
- Compliance: A.8.24 Use of Cryptography
- Backlog record #7 (пам'ять проєкту, 24.07.2026): knowledge-graph
  контекст + knowledge-leakage safeguards
EOF

echo "OK: 0001-ask-ai-alert-panel.md створено"

echo ""
echo "=== Крок 4: docs/threat-models/0001-ask-ai-alert-panel.en.md (English) ==="

cat > docs/threat-models/0001-ask-ai-alert-panel.en.md << 'EOF'
# Threat Model: Ask AI About This Alert Panel

---
feature: Ask AI about this alert panel
date: 2026-07-25
status: draft
---

## Component and Trust Boundaries

Planned feature: user clicks an alert (Sentinel/Defender/ATT&CK coverage
gap) on the Security Dashboard → a Django view collects JSON context
(coverage matrix, alert details, HTTP anomalies) → sends it to the Claude
API → the response (explanation + suggested Terraform fix) is rendered
back to the user in the browser.

Trust boundaries crossed:
1. User's browser → Django view (standard, already covered by MSAL/CIAM auth)
2. Django view → external Claude API (NEW boundary — data leaves the
   Azure perimeter)
3. Claude API response → rendering in the browser (potential XSS surface
   if the response contains unescaped HTML/markdown)
4. Suggested Terraform fix → potential further application by a human
   (NOT automated apply — a critical boundary that must remain manual)

## STRIDE Analysis

### Spoofing
Someone could forge the alert_id parameter in a request to the view,
causing the system to collect and send SOMEONE ELSE'S alert context (or
simulated cross-tenant data) to the Claude API. Mitigation: verify that
alert_id belongs to the current authenticated session/workspace; never
accept an arbitrary ID without validating it against the real Sentinel
workspace.

### Tampering
If the JSON context is assembled from multiple sources (coverage matrix +
live Sentinel alert + HTTP anomalies), someone with intermediate network/
log access could theoretically tamper with data before it reaches the
prompt. Mitigation: all collection happens server-side via already
authenticated MSI calls (Log Analytics), with no client-side proxying.

### Repudiation
There is no audit trail of which suggested fixes the AI panel has ever
generated, or whether anyone applied them. This is a direct, still-open
gap — a MUST HAVE before release: log every request (who, when, which
alert_id, what response) to a dedicated table/AppTraces entry.

### Information Disclosure — MOST CRITICAL SECTION
- Sentinel alert data (possibly including real IPs, User-Agent strings,
  usernames) leaves the Azure perimeter and goes to the external Claude
  API. This requires an explicit decision: is it acceptable to send this
  data externally, or is prior PII redaction/anonymization required?
- Risk that structured context (Terraform resource names, subnet ranges,
  subscription ID) becomes part of a request to a third-party service.
  Mitigation: minimize context to the necessary minimum; do NOT include
  raw secrets or full Terraform files — only summarized facts
  (technique_id, status, a short control/detection text).
- Knowledge leakage in the opposite direction: the AI may "guess" details
  of the architecture from its training data and present the guess as
  fact about THIS system — requires explicit tracing of every claim back
  to a specific field in the input JSON.

### Denial of Service
No rate limiting exists on the new endpoint — theoretically, anyone with
Security Dashboard access could spam requests to the Claude API, causing
unpredictable cost/latency. Mitigation: rate limit at the view level
(e.g. django-ratelimit) plus a short TTL cache for identical alert_ids.

### Elevation of Privilege
The most critical requirement: the MSI/service performing this call must
have STRICTLY read-only access to the Log Analytics/Sentinel API. The
suggested Terraform fix must NEVER be automatically applied (`terraform
apply`) without an explicit, separate, manual human action — the Claude
API here only generates recommendation TEXT, it never executes any
infrastructure changes. A verification step (confirming that any
Terraform resources mentioned in the suggestion actually exist in the
current state) must run BEFORE the response is shown to the user, not
after.

## Identified Action Items

- [ ] Validate alert_id against the real workspace before collecting context
- [ ] Audit-log every AI request (who/when/what) → relates to A.8.15 Logging
- [ ] Explicit decision on PII redaction in context before sending to the Claude API
- [ ] Rate limiting on the endpoint
- [ ] Verify mentioned Terraform resources against the real state before showing the recommendation
- [ ] Explicit MSI role: read-only only (Log Analytics Reader, Security Reader) — NEVER write/Contributor
- [ ] Explicit citation of the source (which JSON field) for every claim in the AI's response

## Related Records

- Compliance: A.8.15/A.8.16 Logging & Monitoring (docs/compliance/0015, 0016)
- Compliance: A.8.24 Use of Cryptography
- Backlog record #7 (project memory, 24.07.2026): knowledge-graph context
  + knowledge-leakage safeguards
EOF

echo "OK: 0001-ask-ai-alert-panel.en.md created"

echo ""
echo "============================================================"
echo "Готово / Done. Review, then commit:"
echo ""
echo "  git add docs/threat-models/"
echo "  git status"
echo "  git commit -m \"Add bilingual (UA/EN) STRIDE threat model template and first analysis\""
echo "  git push origin develop"
echo "============================================================"
