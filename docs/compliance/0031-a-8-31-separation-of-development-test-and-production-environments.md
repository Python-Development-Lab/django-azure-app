---
control_id: A.8.31
regulation: ISO/IEC 27001:2022 Annex A
title: Separation of Development, Test and Production Environments
status: partial
date: 2026-07-25
---

## Description

Development, testing and production environments should be separated and secured.

## Evidence

A dedicated staging environment (app-django-azure-staging) exists and is distinct from local development.

## Gaps

No dedicated, separate production environment currently exists — only staging. This is a known, previously identified open gap.
