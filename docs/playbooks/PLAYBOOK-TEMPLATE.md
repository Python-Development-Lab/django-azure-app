# Incident Response Playbook Template

> Structure adapted from [austinsonger/Incident-Playbook](https://github.com/austinsonger/Incident-Playbook)
> (MIT License), simplified for a single-maintainer project scope.
> Process model: hybrid SANS + NIST Incident Response Process.

---
mitre_technique: <T-number>
mitre_tactic: <Tactic name>
detection_rule: <name of the Sentinel analytics rule that triggers this playbook>
severity: <Low | Medium | High | Critical>
status: draft
last_reviewed: <YYYY-MM-DD>
---

## Preparation

*Note: unlike a top-level "Preparation" phase, each playbook embeds its own
Preparation section — this playbook should be self-contained and usable
without relying on external prerequisites being remembered separately.*

- Detection rule: `<name>` (link to `security/sentinel/analytics-rules/*.tf`)
- Required access: <e.g. Log Analytics Reader, Security Reader, Key Vault access>
- Relevant KQL saved query: <link or inline>

## Identification

*Confirm the signal is real before acting. Steps can run in parallel across
people/teams where possible — this playbook is not purely sequential.*

- [ ] Step 1
- [ ] Step 2

## Containment

*Consider the timing and tradeoffs of containment actions — your response
has consequences (e.g. blocking a legitimate IP, locking out a real user).*

- [ ] Tactical (immediate):
- [ ] Strategic (longer-term):

## Eradication

- [ ] Tool/procedure:

## Recovery

- [ ] Verify normal operation restored
- [ ] Confirm no residual access for the threat actor

## Communication

- [ ] Who is notified, and at what severity threshold?

## Post-Incident Report

- **Executive Summary**: brief description of impact, actions taken, root cause
- **Key metrics**: Time To Detect (TTD), Time To Respond (TTR), Time To Recover (TTR)
- **Timeline**: adversary actions mapped to MITRE ATT&CK tactics
- **Timeline**: response team actions
- **Root Cause Analysis** and recommendations

## Battle Card (quick reference during a live incident)

| Investigate | Contain | Communicate | Recover | Lessons Learned |
|---|---|---|---|---|
| | | | | |
