---
control_id: A.8.15
regulation: ISO/IEC 27001:2022 Annex A
title: Logging
status: implemented
date: 2026-07-25
---

## Description

Logs that record activities, exceptions, faults and other relevant events should be produced, stored, protected and analysed.

## Evidence

AppServiceHTTPLogs, AppTraces, SecurityAlert, AzureActivity, Key Vault AuditEvent, and PostgreSQL PostgreSQLLogs/PostgreSQLFlexSessions are all centralized in Log Analytics workspace law-django-azure-staging via diagnostic settings.
