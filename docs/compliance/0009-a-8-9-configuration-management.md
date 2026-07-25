---
control_id: A.8.9
regulation: ISO/IEC 27001:2022 Annex A
title: Configuration Management
status: implemented
date: 2026-07-25
---

## Description

Configurations, including security configurations, of hardware, software, services and networks should be established, documented, implemented, monitored and reviewed.

## Evidence

All infrastructure is defined in Terraform across 5 modules (network, key_vault, database, app_service, monitoring) with remote state.
