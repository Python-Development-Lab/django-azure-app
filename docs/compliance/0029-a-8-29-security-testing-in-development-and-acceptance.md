---
control_id: A.8.29
regulation: ISO/IEC 27001:2022 Annex A
title: Security Testing in Development and Acceptance
status: implemented
date: 2026-07-25
---

## Description

Security testing processes should be defined and implemented in the development life cycle.

## Evidence

OWASP ZAP (DAST), Trivy (filesystem and IaC config scanning), and Bandit (SAST) all run automatically within the CI/CD pipeline.
