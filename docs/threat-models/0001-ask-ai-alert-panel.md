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
