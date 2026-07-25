---
control_id: A.8.19
regulation: ISO/IEC 27001:2022 Annex A
title: Installation of Software on Operational Systems
status: implemented
date: 2026-07-25
---

## Description

Procedures and measures should be implemented to securely manage software installation on operational systems.

## Evidence

All deployments occur exclusively through the CI/CD pipeline and Terraform; no manual installation on production/staging occurs outside this path.
