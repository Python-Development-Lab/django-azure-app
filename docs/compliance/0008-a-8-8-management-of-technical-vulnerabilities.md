---
control_id: A.8.8
regulation: ISO/IEC 27001:2022 Annex A
title: Management of Technical Vulnerabilities
status: implemented
date: 2026-07-25
---

## Description

Information about technical vulnerabilities of information systems in use should be obtained, exposure evaluated, and appropriate measures taken.

## Evidence

Bandit (SAST), pip-audit, Trivy (filesystem + IaC config), and GitHub Dependabot alerts are all active; known cryptography package CVEs are tracked in GitHub Issue #1.
