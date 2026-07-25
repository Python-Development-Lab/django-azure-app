---
control_id: A.8.21
regulation: ISO/IEC 27001:2022 Annex A
title: Security of Network Services
status: partial
date: 2026-07-25
---

## Description

Security mechanisms, service levels and service requirements of network services should be identified, implemented and monitored.

## Evidence

NSG inbound rules are explicit (AllowHTTPS, DenyAll).

## Gaps

Outbound traffic relies on Azure's implicit default rules rather than an explicit, documented outbound security policy (confirmed during the 24.07.2026 NAT Gateway investigation).
