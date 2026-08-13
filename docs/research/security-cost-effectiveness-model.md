# Security Investment Cost-Effectiveness Model

**Spec:** `docs/specs/security-investment-cost-effectiveness-model.spec.md`
**Purpose:** verified, resource-attributed correlation between candidate remediation actions, their cost, and their actual Secure Score impact for `django-azure-app` specifically -- not the subscription as a whole.

This is a periodic, manually-run report (re-run before priority reviews), not a live dashboard feature. See spec section 3 (Scope) and Open Question 1.

---

## How to re-run this analysis

```bash
mkdir -p /tmp/secscore

az rest --method get \
  --url "https://management.azure.com/subscriptions/23ee341e-dbd1-4904-8bb2-5dde59747b5d/providers/Microsoft.Security/assessments?api-version=2020-01-01" \
  -o json > /tmp/secscore/all_assessments.json

az rest --method get \
  --url "https://management.azure.com/subscriptions/23ee341e-dbd1-4904-8bb2-5dde59747b5d/providers/Microsoft.Security/secureScoreControls?api-version=2020-01-01" \
  -o json > /tmp/secscore/all_controls.json

# Review every returned assessment individually -- do NOT filter by
# displayName regex (e.g. testing for "vulnerability"). Learned
# 13.08.2026: individual assessment displayNames are specific strings
# like "Update gdown", not the category name -- a regex filter on the
# category name returns zero false-negative results and misses real
# findings. Enumerate everything and manually attribute by resourceId
# prefix instead.
jq -r '.value[] | {name: .properties.displayName, status: .properties.status.code, resourceId: .properties.resourceDetails.Id}' /tmp/secscore/all_assessments.json
```

---

## Candidate Action Records

### Action: `update-cryptography-package`

```json
{
  "action_id": "update-cryptography-package",
  "description": "Update outdated `cryptography` package (currently pinned at 41.0.7 due to GLIBC 2.31 constraint), closing 7 Dependabot alerts (4 High, 2 Moderate, 1 Low)",
  "cost": {
    "recurring_monthly_usd": 0,
    "recurring_source": "no new Azure resource required -- pure dependency bump",
    "implementation_hours_estimate": null,
    "implementation_hours_source": "not yet estimated -- blocked on resolving the GLIBC 2.31 base-image constraint (GitHub Issue #1), not just a version bump"
  },
  "secure_score_impact": {
    "category_guid": null,
    "category_name": "Remediate vulnerabilities",
    "points_available_in_category": null,
    "points_current_in_category": null,
    "verified_resources_affected": [],
    "verification_date": "2026-08-13",
    "verification_method": "az rest GET .../providers/Microsoft.Security/assessments (subscription scope), manual review of all 7 returned records -- a regex filter on displayName for \"vulnerability\" was tried first and incorrectly returned 0 results (see note above); direct enumeration of all records was used instead and is the reliable method going forward."
  },
  "qualitative_value": {
    "attck_technique_closed": null,
    "iso27001_control": null
  }
}
```

**Finding (REQ-01, REQ-02):** All 7 `Unhealthy` vulnerability assessments currently in the subscription belong to `hornetdashboardprod`'s container registry (`rg-hornet-dashboard-prod/.../registries/hornetdashboardprod`), for packages `gdown`, `requests`, `tornado`, `streamlit`, `wheel`, `jaraco.context`, and `linux` -- none of which are `django-azure-app` dependencies, and none of which reference `rg-django-azure-staging`.

**Conclusion:** `django-azure-app` currently has **zero** unhealthy resources in the "Remediate vulnerabilities" Secure Score category. Updating the `cryptography` package in this project will **not** move this specific Secure Score category, because the category's current point deficit is entirely attributable to a different project sharing the same subscription.

**This corrects the original 28.07.2026 claim** ("updating `cryptography` would raise Secure Score from 36% to ~67%") with a verified statement rather than a category-name-matching assumption. The `cryptography` update remains worthwhile for its own sake (7 real Dependabot alerts, GLIBC constraint tracked in GitHub Issue #1) -- it is simply decoupled from any Secure Score point claim until a resource-level check says otherwise.

**Status per spec REQ-09:** insufficient data to rank -- cost/effort estimate not yet done (blocked on the GLIBC base-image work), and the verified Secure Score point gain is confirmed to be **zero** for this specific category. Excluded from any ranked output until/unless a different Secure Score category is found to be affected.

---

### Action: `waf-application-gateway`

*(pending -- category identification and resource-level verification not yet run; see Batch 1 continuation)*

### Action: `rbac-scope-down`

*(pending)*

### Action: `postgresql-least-privilege`

*(pending)*

---

## Revision Log

| Date | Change | Reason |
|---|---|---|
| 13.08.2026 | Initial verified record for `update-cryptography-package`, correcting the 28.07.2026 unverified 36%->67% Secure Score claim | Batch 1 of the spec's task breakdown (REQ-01, REQ-02, REQ-03) -- first real output of the model, addressing the exact problem statement that motivated the spec |
