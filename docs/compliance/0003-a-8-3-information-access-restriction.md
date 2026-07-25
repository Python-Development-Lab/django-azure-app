---
control_id: A.8.3
regulation: ISO/IEC 27001:2022 Annex A
title: Information Access Restriction
status: implemented
date: 2026-07-25
---

## Description

Access to information and other associated assets should be restricted in accordance with the established access control policy.

## Evidence

RBAC via Microsoft Entra ID, Key Vault access restricted to System-Assigned Managed Identity only, NSG deny-all on inbound traffic.
