# Playbook: T1110 — Brute Force (HTTP Login)

> Structure adapted from [austinsonger/Incident-Playbook](https://github.com/austinsonger/Incident-Playbook)
> (MIT License).

---
mitre_technique: T1110
mitre_tactic: Credential Access
detection_rule: HTTP Brute Force - Repeated Auth Failures on /auth/login/
severity: Medium
status: draft
last_reviewed: 2026-07-25
---

## Preparation

- Detection rule: `HTTP Brute Force - Repeated Auth Failures on /auth/login/`
  (5-minute window, threshold >10 failures from a single `CIp`)
- Required access: Log Analytics Reader on `law-django-azure-staging`
- Saved KQL:
```kql
  AppServiceHTTPLogs
  | where TimeGenerated > ago(1h)
  | where ScStatus in (401, 403)
  | where CsUriStem == "/auth/login/"
  | summarize FailCount = count() by CIp
  | where FailCount > 10
  | sort by FailCount desc
```
- Known gap: this rule only catches single-IP brute force. Distributed
  password spray (many IPs, low count each) requires the separate
  detection documented in project backlog (see memory record #9).

## Identification

- [ ] Confirm `FailCount` and time window in the Sentinel incident match
      the query above (not a stale/duplicate alert)
- [ ] Check MDTI (`ThreatIntelIndicators`) for a match on the offending IP:
```kql
  ThreatIntelIndicators
  | where IsActive == true
  | where ObservableValue == "<CIp>"
```
  Absence of a match is not a false-positive signal — cloud-range IPs
  rarely appear in curated feeds (confirmed empirically 24.07.2026).
- [ ] Rule out a legitimate cause (QA test run, forgotten-password
      loop by a real user) before treating as hostile.

## Containment

- [ ] Tactical: no WAF/IP-blocking capability currently exists at the
      edge (ADR: `docs/adr/0001-nsg-flow-logs-rejected.md` context;
      T1595 gap tracked separately). Interim option: temporarily adjust
      NSG rule on `app-subnet` if the source IP is static — evaluate
      impact on legitimate traffic first.
- [ ] Strategic: prioritize closing the T1595 WAF gap
      (Application Gateway v2 + WAF, per `docs/adr/0002-nat-gateway-deferred.md`
      cross-reference) if this technique recurs.

## Eradication

- [ ] If a specific account was targeted successfully, force session
      revocation for that account (currently manual — automated
      `revokeSignInSessions` playbook not yet implemented, see backlog).

## Recovery

- [ ] Confirm `FailCount` for the offending IP has dropped to zero in
      subsequent windows.
- [ ] Confirm no successful (`2xx`) logins occurred from the offending IP
      during the attack window:
```kql
  AppServiceHTTPLogs
  | where CIp == "<offending IP>"
  | where CsUriStem == "/auth/login/"
  | where ScStatus == 200
```

## Communication

- [ ] Single IP, <50 failures, no successful login: log only, no escalation.
- [ ] Any successful login following a failure cluster: escalate immediately.

## Post-Incident Report

- **Executive Summary**:
- **TTD / TTR / TTR**:
- **Timeline (adversary)**:
- **Timeline (response)**:
- **Root Cause Analysis**:

## Battle Card

| Investigate | Contain | Communicate | Recover | Lessons Learned |
|---|---|---|---|---|
| Run saved KQL above; check MDTI match | No WAF yet — manual NSG adjustment only | Escalate only if a login succeeded | Confirm FailCount = 0 in next window | Update this playbook after every real trigger |
