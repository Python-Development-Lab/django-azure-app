---
control_id: A.8.24
regulation: ISO/IEC 27001:2022 Annex A
title: Use of Cryptography
status: implemented
date: 2026-07-25
---

## Description

Rules for the effective use of cryptography, including cryptographic key management, should be defined and implemented.

## Evidence

All application secrets are stored exclusively in Azure Key Vault (Private Endpoint), accessed only via System-Assigned Managed Identity. Encryption at rest is enabled by default on PostgreSQL Flexible Server.

## Gaps

No formal, documented cryptographic policy (approved algorithms, key rotation schedule) exists yet — current implementation is sound but undocumented as an explicit policy.
