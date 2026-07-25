---
control_id: A.8.2
regulation: ISO/IEC 27001:2022 Annex A
title: Privileged Access Rights
status: partial
date: 2026-07-25
---

## Description

The allocation and use of privileged access rights should be restricted and managed.

## Evidence

MSI roles are scoped per service (Key Vault Secrets User, Cost Management Reader, Security Reader, Log Analytics Reader). human_admin_object_id separates the maintainer's personal Key Vault access from CI service-principal rotation.

## Gaps

No formal Privileged Identity Management (PIM) with time-bound elevation is configured yet.
