---
title: NSG Flow Logs — свідомо не реалізовано
status: rejected
date: 2026-07-24
---

## Чому

App Service regional VNet integration архітектурно приховує внутрішній
трафік (App Service → Key Vault / PostgreSQL) від NSG flow logs —
підтверджено офіційною документацією Microsoft. Витрачати ресурси
(Storage Account, Traffic Analytics) на логи, які не покажуть саме той
трафік, заради якого їх вмикають, недоцільно.

## Альтернатива

Замінено на diagnostic settings напряму на ресурсах: Key Vault AuditEvent
(SecretGet, Authentication) + PostgreSQL PostgreSQLLogs /
PostgreSQLFlexSessions — дає точнішу видимість (хто, коли, яка операція,
з якою ідентичністю) через таблицю AzureDiagnostics.
