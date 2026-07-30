# Spec: Continuous Risk-Scoring MVP (Weighted Signal Aggregation)

**Status:** Draft
**Feature ID:** `SEC-ZEROTRUST-RISKSCORE-01`
**Related backlog item:** Zero Trust Policy Enforcement Point gap — `RiskScoringMiddleware` has been aspirational since 25.07.2026 (confirmed as descriptive text only, not real code); this spec is a deliberately scoped-down first real implementation, proposed 28.07.2026
**Owner:** Vitalii Shevchuk
**Target surface:** new function/service in `core/views.py` or a new module (e.g., `core/risk_scoring.py`), Security Dashboard display, `security/mitre/attack_data.json` (status review only)

---

## 1. Overview

Build a genuinely minimal risk-scoring MVP that aggregates three **already-existing** signals — the device anomaly flag from `DeviceVerificationMiddleware`, the HTTP anomaly match from `_get_http_anomalies()`, and the confidence score from `_get_threat_intel_data()` — into a single, simple, documented weighted score (0-100) per session, displayed on the Security Dashboard. This is explicitly **not** the full KBSSE/fuzzy-topology approach (Lakhno et al., 2020) already cited in this project's academic background, and **not** the historically-aspirational `RiskScoringMiddleware` concept in its full form — it is a small, real, honestly-scoped first step, chosen specifically to stop the false-assurance pattern of naming a control that doesn't exist as code.

## 2. Problem Statement

`security/mitre/attack_data.json` currently has 4 techniques (`T1068`, `T1110.004`, `T1528`, and likely `T1567`) whose `control`/`detection` text references `RiskScoringMiddleware` — a component confirmed (25.07.2026 session, re-confirmed via direct file read 28.07.2026) to exist only as descriptive text, not real code. Per `CONSTITUTION.md` Rule #3, this is exactly the class of false-assurance claim this project's own methodology exists to prevent. Two paths exist: (a) correct the labels to honestly say `gap` and stop there, or (b) build something small and real that genuinely earns a non-`gap` status for at least part of this claim. This spec pursues (b), scoped deliberately small enough to actually ship, rather than repeating the mistake of aiming for the full aspirational concept and never finishing it.

## 3. Scope

**In scope:**
- A single scoring function combining exactly 3 already-existing inputs (see Data Model) into one weighted score, 0-100
- A simple, fixed, fully documented weighting formula — no machine learning, no fuzzy topology
- Displaying the score and its component breakdown on the Security Dashboard, reusing the existing HTMX bundle pattern
- An honest review of `attack_data.json`'s `T1068`/`T1110.004`/`T1528`/`T1567` entries once this MVP exists, to accurately reflect what it does and does not cover

**Out of scope (explicitly deferred):**
- The full Lakhno et al. fuzzy-topology / weighted Hamming distance method — a real, citable, more rigorous approach, but too large a lift for a first MVP; noted as a future upgrade path only if this MVP proves valuable and insufficient on its own
- Any machine learning model or training pipeline
- Any automated action triggered by the score (e.g., auto-blocking, auto-escalation) — this MVP only computes and displays a number; per `CONSTITUTION.md`'s caution against automating consequential actions without hard guardrails already in place, acting on this score is a separate, future, much more carefully-scoped decision
- Real-time/continuous per-request recalculation — this MVP computes the score on-demand (Security Dashboard load), not as a live streaming pipeline
- Renaming this MVP "`RiskScoringMiddleware`" — it is deliberately a smaller, different, honestly-named thing; that historical name should only be reconsidered if this MVP is later expanded significantly

## 4. Data Model

```json
{
  "account_upn": "...",
  "score": 42,
  "computed_at": "2026-07-28T12:00:00Z",
  "components": {
    "device_anomaly": {
      "value": true,
      "weight": 34,
      "contribution": 34,
      "source": "DeviceVerificationMiddleware"
    },
    "http_anomaly_match": {
      "value": false,
      "weight": 33,
      "contribution": 0,
      "source": "_get_http_anomalies()"
    },
    "mdti_confidence": {
      "value": 80,
      "weight": 33,
      "contribution": 26,
      "source": "_get_threat_intel_data() / ThreatIntelIndicators.Confidence"
    }
  }
}
```

Each component's `contribution` is `value_normalized_to_0_1 × weight`. Weights sum to 100 by design (34 + 33 + 33). If a component is unavailable, its weight is excluded and the remaining weights are re-normalized (see REQ-03).

## 5. Requirements (EARS notation)

### 5.1 Score computation

- **REQ-01 (Ubiquitous):** The system shall compute a risk score (0-100) for a given account/session by combining exactly 3 inputs: the device anomaly flag, the HTTP anomaly match, and the MDTI confidence value, per the Data Model in section 4.
- **REQ-02 (Ubiquitous):** The weighting formula shall be a fixed, explicit, documented weighted sum — no machine learning, no undocumented heuristics.
- **REQ-03 (Unwanted behavior):** If one of the 3 inputs is unavailable (e.g., the MDTI query fails or times out), then the system shall compute the score using only the available inputs, with weights re-normalized to still sum to 100 — never fail the entire computation, and never silently treat a missing input as zero risk.

### 5.2 Display

- **REQ-04 (Ubiquitous):** The Security Dashboard shall render the computed score alongside its full component breakdown — a bare number without the "why" is not acceptable, per this project's established citation/traceability discipline (see `ask-ai-alert-panel.spec.md` REQ-04 for the same principle applied elsewhere).
- **REQ-05 (Optional feature):** Where the score exceeds an operator-configured threshold, the display shall visually flag it (e.g., color coding) — but this flagging shall **not** trigger any automated action, per this spec's Out of Scope boundary.

### 5.3 Honest scope and labeling (the core reason this spec exists)

- **REQ-06 (Unwanted behavior):** If this MVP is referenced anywhere in `attack_data.json`'s `control` or `detection` text, then it shall be described accurately as a minimal, weighted-sum risk-score MVP — never as "`RiskScoringMiddleware`" or worded to imply the full KBSSE/fuzzy-topology approach, to avoid repeating the exact false-assurance pattern already found and corrected this session.
- **REQ-07 (Event-driven):** When this MVP is implemented and verified working, the `T1068`, `T1110.004`, `T1528`, and `T1567` entries in `attack_data.json` shall be reviewed and their `status`/`control`/`detection` text updated to reflect what this MVP genuinely covers — likely remaining `gap` or moving to a new, honestly-described intermediate status, **not** jumped straight to `detected` unless the MVP's actual coverage genuinely justifies that per `CONSTITUTION.md` Rule #3.

## 6. Non-Functional Requirements

- **NFR-01:** Reuses existing signal sources (`_get_http_anomalies()`, `_get_threat_intel_data()`, `DeviceVerificationMiddleware`) — no new Azure resources, no new data source, no new MSI role grant. The existing roles already cover the needed reads.
- **NFR-02:** Computing this score on Security Dashboard load shall not meaningfully regress existing load times — follow the same caching discipline already established for `_all_cost_data()` (bundle + cache, not a new uncached call path).

## 7. Task Breakdown

| Batch | REQs covered | Description | Depends on | Azure write required? |
|---|---|---|---|---|
| 1 | REQ-01, REQ-02, REQ-03 | Core scoring function, reusing existing signal sources, with graceful degradation for missing inputs | - | No |
| 2 | REQ-04, REQ-05 | Security Dashboard display (score + component breakdown + threshold-based visual flag) | Batch 1 | No |
| 3 | REQ-06, REQ-07 | Honest labeling check + review/update of `attack_data.json`'s 4 affected technique entries | Batch 1, 2 verified working | No |

## 8. Acceptance Criteria (checklist)

- [ ] Score correctly combines all 3 available inputs using the documented fixed-weight formula (REQ-01, REQ-02)
- [ ] Missing-input case handled via re-normalization, not silent zero or hard failure (REQ-03)
- [ ] Dashboard shows score + full component breakdown, not a bare number (REQ-04)
- [ ] Threshold-based visual flag present; confirmed to trigger no automated action (REQ-05)
- [ ] No reference to "RiskScoringMiddleware" or KBSSE/fuzzy-topology language anywhere describing this MVP (REQ-06)
- [ ] `attack_data.json`'s 4 affected entries reviewed and honestly updated after implementation, not left stale (REQ-07)

## 9. Open Questions

1. What specific weights should the 3 components use? **Recommendation:** start with roughly equal weights (34/33/33) as a defensible, simple default — do not invent sophisticated weighting without evidence. Revisit and calibrate only once real data from actual documented incidents (the NMap scan, Zero Trust device alerts) is available to check whether equal weighting produced sensible scores in hindsight.
2. When (if ever) to graduate this MVP toward the full Lakhno et al. fuzzy-topology method? **Recommendation:** explicitly deferred — revisit only if this MVP proves genuinely useful in practice and the gap techniques it partially addresses remain unresolved by this simpler approach after a reasonable trial period.

## 10. Traceability

This spec reuses code from the existing `security_alerts` view path (`_get_http_anomalies()`, `_get_threat_intel_data()`) and `auth_app.device_middleware` (`DeviceVerificationMiddleware`) — no new data source. It directly implements `CONSTITUTION.md` Rule #3 (Security Claims & Documentation Integrity) by existing specifically to close a false-assurance gap rather than perpetuate it. It references the already-cited academic work (Lakhno, Kasatkin, Blozva, Misiura, Husiev, 2020) as the acknowledged, more rigorous future direction this MVP deliberately does not attempt yet. Independent of Groups A/C in `docs/specs/README.md`; belongs in Group B alongside the other independent feature specs.

## Revision Log

| Date | Change | Reason |
|---|---|---|
| 28.07.2026 | Initial draft created, scoped deliberately as a minimal MVP rather than the full aspirational `RiskScoringMiddleware`/KBSSE concept | Direct response to this session's repeated finding that `RiskScoringMiddleware` is referenced in `attack_data.json` but does not exist as real code — this spec exists to either close that gap honestly and minimally, or to make clear via REQ-06/REQ-07 that it remains open |

---

## Requirement Traceability Verification (fill in only after implementation)

**Do not populate this section while authoring the spec.** Prompt to use for this pass:

> Audit the completed implementation against `docs/specs/continuous-risk-scoring-mvp.spec.md`. For every requirement REQ-01 through REQ-07, provide: Status (satisfied / partially satisfied / missing), implementation file and symbol, test/verification evidence.

| REQ | Status | Implementation (file:symbol) | Test/Verification | Notes |
|---|---|---|---|---|
| REQ-01 | — | — | — | — |
| REQ-02 | — | — | — | — |

Only change this spec's **Status** field from `Draft` to `Implemented` once this table is fully populated and every requirement is `satisfied`.