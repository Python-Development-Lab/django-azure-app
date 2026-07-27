# Threat Model Template (STRIDE)

> Fill in BEFORE implementing the feature, not after — aligned with the
> Spec-Driven Development principle (specification/analysis before code).

---
feature: <feature name>
date: <YYYY-MM-DD>
status: draft
---

## Component and Trust Boundaries

<Describe the component and every trust boundary it crosses — e.g.
"user's browser → Django view → external API → database". Each
boundary is a potential attack point.>

## STRIDE Analysis

### Spoofing
<Can someone impersonate a legitimate user/service/data source?>

### Tampering
<Can someone modify data/code/configuration without authorization?>

### Repudiation
<Can someone deny an action without sufficient evidence/logs?>

### Information Disclosure
<Can confidential information reach unintended recipients?>

### Denial of Service
<Can someone make the component/system unavailable?>

### Elevation of Privilege
<What role/MSI/permissions will this component have? Is there a risk
of obtaining higher privileges than intended?>

## Identified Action Items

- [ ] <Action 1> → related MITRE ATT&CK technique (if relevant): T____
- [ ] <Action 2>

## Related Records

- ADR: <link to docs/adr/*.md, if any>
- Compliance: <link to docs/compliance/*.md, if any>
- Playbook: <link to docs/playbooks/*.md, if any>
