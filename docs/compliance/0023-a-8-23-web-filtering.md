---
control_id: A.8.23
regulation: ISO/IEC 27001:2022 Annex A
title: Web Filtering
status: gap
date: 2026-07-25
---

## Description

Access to external websites should be managed to reduce exposure to malicious content.

## Evidence

(none — see Gaps)

## Gaps

No WAF or IP restrictions currently sit in front of the application. This is an explicitly identified, high-priority open backlog item, mapped to MITRE ATT&CK T1595. Application Gateway v2 + WAF has been selected as the preferred implementation path over Azure Front Door (see docs/adr/).
