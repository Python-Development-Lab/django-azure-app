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

# CRITICAL (added 13.08.2026 after a real methodology failure -- see
# the CORRECTION note on the cryptography record below): this API
# response is PAGINATED. Check for a .nextLink field and follow it
# until absent before drawing any conclusion. A single-page read
# missed 7 of 118 real records and produced a wrong conclusion that
# was merged and had to be corrected. Loop example:

NEXTLINK=$(jq -r ".nextLink // empty" /tmp/secscore/all_assessments.json)
PAGE=2
> /tmp/secscore/all_pages_combined.json
echo "[]" > /tmp/secscore/all_pages_combined.json
while [ -n "$NEXTLINK" ]; do
  az rest --method get --url "$NEXTLINK" -o json > "/tmp/secscore/page_${PAGE}.json"
  jq -s ".[0] + .[1].value" /tmp/secscore/all_pages_combined.json "/tmp/secscore/page_${PAGE}.json" > /tmp/secscore/tmp.json
  mv /tmp/secscore/tmp.json /tmp/secscore/all_pages_combined.json
  NEXTLINK=$(jq -r ".nextLink // empty" "/tmp/secscore/page_${PAGE}.json")
  PAGE=$((PAGE + 1))
  sleep 1
done
# /tmp/secscore/all_pages_combined.json now holds every page-2+ record;
# combine with page 1's .value array before filtering by resource group.
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

**CORRECTION (13.08.2026) -- the finding below was wrong. Original text preserved with strikethrough for the record, per this project's honest-documentation principle.**

~~Finding (REQ-01, REQ-02): All 7 Unhealthy vulnerability assessments currently in the subscription belong to hornetdashboardprod's container registry, none reference rg-django-azure-staging. Conclusion: django-azure-app currently has zero unhealthy resources in the "Remediate vulnerabilities" category.~~

**What went wrong:** the `Microsoft.Security/assessments` API response is **paginated** (`nextLink`), and the original query only read page 1 of 6 (7 of 118 total records). The methodology fix from the original REQ-01/REQ-02 pass (verify resource attribution, don't trust category names) was correct, but it was undermined by a *different* verification gap: not confirming the API response was complete before drawing a conclusion from it.

**Corrected finding, all 6 pages (118 total records) enumerated:** `rg-django-azure-staging` has confirmed `Unhealthy` assessments for **both** `Update Django` and `Update cryptography`, against resource `/subscriptions/23ee341e-dbd1-4904-8bb2-5dde59747b5d/resourceGroups/rg-django-azure-staging/providers/Microsoft.Web/sites/app-django-azure-staging`.

**Corrected conclusion:** this project **does** have at least one real, resource-attributed vulnerability finding for `cryptography`. Whether fixing it moves the "Remediate vulnerabilities" Secure Score category specifically is **not yet confirmed** -- REQ-01 through REQ-03 require verifying the Secure Score *category* attribution too (via `secureScoreControlDefinitions` or an equivalent mapping from assessment type to control), which this pass did not complete (`secureScoreControlDefinitions` returned `Not Found` on the API version tried). The Secure Score point-gain estimate for this action remains open, now for a different reason than before.

**Status per spec REQ-09:** still insufficient data to rank -- resource attribution is now confirmed (unlike the original pass), but the Secure Score category/point mapping and the cost/effort estimate (still blocked on the GLIBC base-image constraint, GitHub Issue #1) remain outstanding. Excluded from any ranked output until both are resolved.

**Methodology note added to this report's "How to re-run" section below:** always check for and follow `nextLink` until it is absent before drawing any conclusion from an `az rest` list response.

---

### Action: `waf-application-gateway`

**Finding (13.08.2026, REQ-01/REQ-02/REQ-03):** Investigated whether Application Gateway v2 + WAF (the T1595-closing candidate already planned in `docs/backlog-status.md`) affects the "Restrict unauthorized network access" Secure Score category (current: 1.33/4 points, 33.25%, `unhealthyResourceCount: 4`).

Cross-referenced the category's underlying `assessmentDefinitions` (via `Microsoft.Security/secureScoreControlDefinitions`) against `rg-django-azure-staging`'s actual Unhealthy findings (from the full, paginated `assessments` list -- see the corrected `update-cryptography-package` record above for why full pagination matters). Three of the category's Unhealthy findings for this project were identified and confirmed to belong to "Restrict unauthorized network access":

| Finding | Resource | Category (verified via secureScoreControlDefinitions) |
|---|---|---|
| Storage account should use a private link connection | `stdjangosarif89420`, `stcostexp02l9xz` | Restrict unauthorized network access |
| Storage accounts should restrict network access using virtual network rules | `stdjangosarif89420`, `stcostexp02l9xz` | Restrict unauthorized network access |
| Firewall should be enabled on Key Vault | `kv-django-azure-staging` | Restrict unauthorized network access |

A fourth related-sounding finding ("Storage account public access should be disallowed", also Unhealthy on `stcostexp02l9xz`) was checked and does **not** belong to this category -- it maps to "Manage access and permissions" instead, per the same `secureScoreControlDefinitions` cross-reference. Included here as a negative-result data point, not a false lead.

**Corrected direction (important scope finding):** none of these three findings are addressed by Application Gateway v2 + WAF. WAF protects HTTP(S) traffic into the web application (the actual purpose of the `waf-application-gateway` action, and the correct fix for the T1595 active-scanning gap) -- it does not touch Storage Account or Key Vault network isolation. The action that would actually move this Secure Score category is a **different, cheaper** one: extending the Private Endpoint pattern already used for PostgreSQL and (partially) Key Vault to both Storage Accounts, plus resolving the Key Vault firewall finding specifically.

**Conclusion:** `waf-application-gateway`'s Secure Score impact on "Restrict unauthorized network access" is likely **near zero** for these three specific findings -- its real value remains the T1595 ATT&CK gap closure (qualitative, not this category's points), which was always the primary justification for it in `docs/backlog-status.md`. A separate, not-yet-named candidate action ("extend Private Endpoints to both Storage Accounts + Key Vault firewall") is the actual cost-effective path to this specific Secure Score category -- not yet added as a full record in this model; recommended as the next candidate to evaluate.

**Status per spec REQ-09:** `waf-application-gateway`'s point-gain estimate for *this* category is effectively ruled out (not "insufficient data" -- a genuine negative finding). Its qualitative ATT&CK/T1595 value is unaffected and remains the actual justification for the action, tracked separately from this Secure-Score-specific ranking per REQ-07.

### Action: `rbac-scope-down`

*(pending)*

### Action: `postgresql-least-privilege`

*(pending)*

---

## Revision Log

| Date | Change | Reason |
|---|---|---|
| 13.08.2026 | Initial verified record for `update-cryptography-package`, correcting the 28.07.2026 unverified 36%->67% Secure Score claim | Batch 1 of the spec's task breakdown (REQ-01, REQ-02, REQ-03) -- first real output of the model, addressing the exact problem statement that motivated the spec |
