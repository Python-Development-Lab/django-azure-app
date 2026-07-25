---
control_id: A.8.18
regulation: ISO/IEC 27001:2022 Annex A
title: Use of Privileged Utility Programs
status: partial
date: 2026-07-25
---

## Description

The use of utility programs that can be capable of overriding system and application controls should be restricted and tightly controlled.

## Evidence

`az rest` is used as a documented workaround for known-broken `az keyvault` / `az role assignment` CLI modules in the Codespace environment.

## Gaps

This workaround is documented as a project learning, but is not governed by a formal privileged-utility-program policy.
