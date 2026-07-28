# Spec: IOC Reputation Lookup for Defender Alerts Panel

**Status:** Draft
**Feature ID:** SEC-DASH-IOC-01
**Related backlog item:** Evidence-Linked ATT&CK Mapping + IOC Reputation Lookup (27.07.2026)
**Owner:** Vitalii Shevchuk
**Target surface:** `core/views.py` (`_get_defender_alerts()` or equivalent), `templates/core/partials/security_alerts.html`

---

## 1. Overview

Enrich the existing `/security/alerts/` panel so that each Defender for Cloud alert's source IP is annotated with a reputation badge (e.g., known malicious / unclassified / known cloud-infrastructure range), sourced from data already reachable through the existing Sentinel/Log Analytics connection. This is a small enrichment to an existing endpoint, not a new panel, new data source onboarding, or investigation tool.

## 2. Problem Statement

`/security/alerts/` already displays live Defender for Cloud alerts including source IPs (e.g., `20.61.126.211` from the NMap scan incident), but gives no context on whether that IP is a known-bad actor, a benign cloud scanner, or unclassified. The analyst currently has to manually look this up elsewhere, breaking the single-pane-of-glass value of the dashboard.

## 3. Scope

**In scope:**
- One enrichment step added to the existing alert-fetching code path
- Reputation lookup limited to IPs already present in returned Defender alerts (no bulk IOC ingestion)
- A single badge per alert row in the existing template
- Aggressive caching (IP reputation does not change minute-to-minute)

**Out of scope (explicitly deferred — this is CTI-workbench territory, not this project's scope):**
- Bulk IOC list management or IOC feed subscription
- Actor/campaign attribution
- Malware sample correlation
- A dedicated investigation workspace or case management UI

## 4. Data Model

No new Django model or database table. Enrichment result is a transient dict attached to each alert at render time, plus a cache entry:

```python
# Cache key pattern
cache_key = f"ioc_reputation:{source_ip}"

# Cached value shape
{
    "source_ip": "20.61.126.211",
    "classification": "known_azure_range",  # one of: "recently_flagged_malicious" | "unclassified" | "known_azure_range"
    "source": "sentinel_threat_intel_indicators",  # or "abuseipdb" if fallback used
    "checked_at": "2026-07-28T10:00:00Z",
    "confidence": null,  # populated from ThreatIntelIndicators.Confidence (0-100) when a match is found
    "valid_from": null,  # populated from ThreatIntelIndicators.ValidFrom when a match is found
    "valid_until": null  # populated from ThreatIntelIndicators.ValidUntil when a match is found
}
```

Example real match (from confirmed live data, 28.07.2026): an alert with source IP `139.135.41.41` would match a `ThreatIntelIndicators` row with `Confidence: 100`, `IndicatorProvider: Microsoft`, tagged `honeypot` + `Botnet`, valid for a ~5-hour window — this becomes `classification: "recently_flagged_malicious"` per REQ-13, not a permanent `"malicious"` label.

## 5. Requirements (EARS notation)

### 5.1 Lookup trigger and source priority

**Implementation note (28.07.2026, corrected post-investigation):** Initial diagnosis queried the deprecated legacy table `ThreatIntelligenceIndicator` (no new data ingested there since July 2025) and found it empty, which was misread as "no TI connector configured." A follow-up query against the **current** table `ThreatIntelIndicators` confirmed the Microsoft Defender Threat Intelligence connector (`BasicMDTIConnector`) is active and populated (10 sample rows returned, all high-confidence (100) botnet/brute-force IP indicators from MSTIC honeypots, each with a short validity window of a few hours). **REQ-02 is functional now and should be implemented as the primary path — no separate connector-enablement backlog item is needed.**

- **REQ-01 (Event-driven):** When `/security/alerts/` is loaded and returns one or more alerts with a source IP, the system shall attempt a reputation lookup for each distinct IP.
- **REQ-02 (Ubiquitous):** The system shall query the `ThreatIntelIndicators` table (not the deprecated `ThreatIntelligenceIndicator` table) via the existing `law-django-azure-staging` Log Analytics connection and existing MSI Security Reader role, filtering on `IsActive == true` and matching `ObservableValue` against the alert's source IP where `ObservableKey` indicates a network/IP observable.
- **REQ-03 (Optional feature):** Where `ThreatIntelIndicators` returns no match for a given IP, the system shall fall back to a single public reputation API call (e.g., AbuseIPDB), if and only if an API key is available via Key Vault.
- **REQ-04 (Unwanted behavior):** If no API key is configured for the fallback source, then the system shall classify the IP as `"unclassified"` rather than failing the request or leaving the panel unrenderable.
- **REQ-13 (Ubiquitous):** Given the short validity window observed in this TI feed (indicators tied to active honeypot-detected botnet activity, often valid for only a few hours), the system shall label a `ThreatIntelIndicators` match as `"recently_flagged_malicious"` rather than a bare `"malicious"`, and shall include the indicator's `ValidFrom`/`ValidUntil` window in the badge tooltip so the operator understands the recency of the match rather than assuming a permanent blocklist entry.

### 5.2 Caching

- **REQ-05 (Ubiquitous):** The system shall cache each IP's reputation result for 24 hours per IP, using a per-IP cache key (not a shared bundle key), following the caching-discipline pattern established for `_all_cost_data()` and the planned Defender-plans badge.
- **REQ-06 (State-driven):** While a cached reputation entry exists and is not expired, the system shall use the cached value and shall not issue a new lookup call for that IP.
- **REQ-14 (Unwanted behavior):** If a `ThreatIntelIndicators` match's `ValidUntil` timestamp is earlier than the standard 24-hour cache TTL would otherwise allow, then the system shall cache that specific result only until `ValidUntil`, not the full 24 hours — given the observed ~5-hour validity windows in this feed, a full 24h cache could serve a stale "recently flagged" badge long after the underlying indicator has expired and no longer reflects Microsoft's current assessment.

### 5.3 Secrets handling

- **REQ-07 (Ubiquitous):** Where a fallback reputation API key is used, the system shall store and retrieve it via Azure Key Vault, following the existing secrets-management pattern (`ManagedIdentityCredential()`, no `client_id`, System-Assigned MSI) — the key shall never be hardcoded or stored in an environment file committed to source control.

### 5.4 Display

- **REQ-08 (Ubiquitous):** The alerts panel shall render one reputation badge per alert row, positioned adjacent to the source IP.
- **REQ-09 (State-driven):** While an IP is classified `"recently_flagged_malicious"`, the badge shall be visually distinct (e.g., red/warning styling) from `"unclassified"` (neutral styling) and `"known_azure_range"` (informational styling).
- **REQ-10 (Unwanted behavior):** If the reputation lookup fails entirely (both primary and fallback sources unreachable), then the panel shall still render the alert row without a badge, rather than failing to render the alert itself — reputation enrichment is additive, not a blocking dependency.

## 6. Non-Functional Requirements

- **NFR-01:** No new Azure resource is required for the primary source (Sentinel `ThreatIntelIndicators` is already reachable via the existing Log Analytics connection and existing MSI role, with the MDTI connector already active).
- **NFR-02:** If the fallback API key is added, the only new Terraform resource is one `azurerm_key_vault_secret`, following the existing pattern — no new compute, storage, or networking resources.
- **NFR-03:** The enrichment step shall not introduce a new HTMX endpoint — it is folded into the existing `_get_defender_alerts()` code path and existing template.
- **NFR-04:** Reputation lookups shall not cause the existing `/security/alerts/` load time to regress by more than a small, acceptable margin (informal target: no more than +500ms on first load per distinct uncached IP; cached loads should show no measurable regression).

## 7. Acceptance Criteria (checklist)

- [ ] Reputation badge appears next to each alert's source IP on `/security/alerts/`
- [ ] `ThreatIntelIndicators` (not the deprecated `ThreatIntelligenceIndicator`) is queried as the primary, working source, filtered on `IsActive == true`
- [ ] A match's short validity window is respected in both classification wording (`"recently_flagged_malicious"`, not bare `"malicious"`) and cache TTL (REQ-14)
- [ ] Fallback to a public API only occurs when a Key Vault-stored key is present; otherwise IP is marked `unclassified` without error
- [ ] Reputation results are cached per-IP for 24 hours
- [ ] The known real test case — `20.61.126.211` (NMap scan source IP) — renders with an appropriate classification (expected: `known_azure_range`, per prior project notes that this IP falls within an Azure address range)
- [ ] A total lookup failure (both sources unreachable) does not break alert rendering
- [ ] No new HTMX endpoint added; no regression to the existing single-bundle-style loading pattern

## 8. Open Questions

1. ~~Whether `ThreatIntelligenceIndicator` in `law-django-azure-staging` currently has any populated threat intelligence data~~ **RESOLVED and CORRECTED (28.07.2026):** initial check queried the deprecated legacy table (`ThreatIntelligenceIndicator`), which Microsoft stopped ingesting into as of July 2025 — its emptiness was a false signal. A follow-up query against the **current** table, `ThreatIntelIndicators`, confirmed the Microsoft Defender Threat Intelligence connector (`BasicMDTIConnector`) is active and populated with high-confidence (100) botnet/brute-force IP indicators from MSTIC honeypots, each with a short (~5 hour) validity window. **REQ-02 is fully functional today.**

2. ~~Whether a paid fallback API is worth the Key Vault secret and Terraform change~~ **REVISED DECISION (28.07.2026, corrected):** given Finding 1 is now positive, implement **REQ-02 (Sentinel `ThreatIntelIndicators`) as the primary, fully-tested path** for this iteration. REQ-03 (public API fallback) remains valuable as a secondary source for IPs not covered by the MDTI honeypot feed (which is botnet/brute-force focused and won't cover every threat category), but is no longer a blocking prerequisite — it can be shipped in a later increment without reducing the feature's value in this iteration.

## 8a. ~~Follow-up backlog item~~ (retracted, 28.07.2026)

The originally proposed backlog item ("investigate enabling a Threat Intelligence data connector") is **not needed** — the MDTI connector is already active and populated, confirmed via direct query against the correct (non-deprecated) table. This section is retained only to document that the investigation was done and the item was retracted, avoiding future re-investigation of the same question.

## 9. Traceability

This spec implements the "IOC Reputation Lookup" half of the 27.07.2026 backlog item. It is independent of the Evidence-Linked ATT&CK Mapping spec (`docs/specs/evidence-linked-attack-mapping.spec.md`) — no shared data model, though both specs originate from the same backlog entry and the same AdversaryGraph article comparison that prompted the scoped-down approach (full CTI-workbench IOC enrichment explicitly rejected as out of scope; see backlog rationale).
