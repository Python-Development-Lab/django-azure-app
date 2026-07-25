---
control_id: A.8.34
regulation: ISO/IEC 27001:2022 Annex A
title: Protection of Information Systems During Audit Testing
status: partial
date: 2026-07-25
---

## Description

Audit tests and other assurance activities involving assessment of operational systems should be planned and agreed between the tester and appropriate management.

## Evidence

OWASP ZAP DAST scans are run against the staging environment as part of the CI/CD pipeline.

## Gaps

No formal, documented audit-testing protection procedure (scheduling, scope agreement, rollback plan) exists beyond the automated pipeline step.
