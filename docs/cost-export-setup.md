# Cost Export Setup — Manual CLI Step

> **Status as of 09.08.2026: NOT YET EXECUTED.** The Terraform module
> (storage account + container + RBAC) is deployed once this PR merges,
> but steps 2-4 below (create the export, wire its identity, set the
> App Setting) have not been run yet. Until step 4 runs,
> `COST_EXPORT_STORAGE_ACCOUNT` is unset and `_fetch_latest_export_csv()`
> always returns `None` -- the dashboard silently stays on the live
> API + `_retry_on_429()` fallback path. This is safe (no broken
> behavior) but means the new infrastructure delivers no benefit until
> someone runs steps 2-4.

Following the repo's own established pattern (manual `az rest` artifact,
formalized in Terraform later — see `kv-to-sentinel`/`pg-to-sentinel`
precedent in backlog history), the Cost Management Export resource itself
is created via CLI, not a Terraform `azurerm_*` resource. Reason: the
exact native `azurerm` resource name/schema for subscription-scope cost
exports varies across provider versions and was not verified against this
repo's pinned version at the time of writing. The storage account,
container, and RBAC are in Terraform (`terraform/modules/cost_export/`);
only the export definition itself is a one-time CLI step below.

## 1. Apply the Terraform module first

Deploy `modules/cost_export` (storage account + container + App Service
reader role) before creating the export, so the destination exists.

```bash
terraform apply -target=module.cost_export
```

## 2. Create the export

```bash
STORAGE_NAME=$(az storage account list \
  --resource-group rg-django-azure-staging \
  --query "[?starts_with(name,'stcostexp')].name" -o tsv)

STORAGE_ID=$(az storage account show \
  --name "$STORAGE_NAME" \
  --resource-group rg-django-azure-staging \
  --query id -o tsv)

az costmanagement export create \
  --name "resource-costs-daily" \
  --scope "/subscriptions/23ee341e-dbd1-4904-8bb2-5dde59747b5d" \
  --type "ActualCost" \
  --timeframe "MonthToDate" \
  --storage-account-id "$STORAGE_ID" \
  --storage-container "cost-exports" \
  --storage-directory "resource-costs" \
  --recurrence "Daily" \
  --schedule-status "Active" \
  --recurrence-period from="2026-08-01T00:00:00Z" to="2027-08-01T00:00:00Z" \
  --definition '{
    "type": "ActualCost",
    "timeframe": "MonthToDate",
    "dataSet": {
      "granularity": "Daily",
      "configuration": {
        "columns": ["Date", "ResourceId", "ResourceGroupName", "CostInBillingCurrency", "BillingCurrency"]
      }
    }
  }'
```

## 3. Wire the export's identity back into Terraform

The export is created with a System-Assigned Identity. Retrieve its
principal ID and feed it back into the Terraform module so it gets
`Storage Blob Data Contributor` on the destination storage account:

```bash
az costmanagement export show \
  --name "resource-costs-daily" \
  --scope "/subscriptions/23ee341e-dbd1-4904-8bb2-5dde59747b5d" \
  --query identity.principalId -o tsv
```

Add this value as `cost_export_identity_principal_id` in
`terraform.tfvars`, then:

```bash
terraform apply -target=module.cost_export
```

## 4. Point the App Service at the storage account

The Django code (`_fetch_latest_export_csv()` in `core/views.py`) reads
`COST_EXPORT_STORAGE_ACCOUNT` from the environment. Set it as an App
Setting:

```bash
az webapp config appsettings set \
  --name app-django-azure-staging \
  --resource-group rg-django-azure-staging \
  --settings COST_EXPORT_STORAGE_ACCOUNT="$STORAGE_NAME" \
  --output none
```

(`--output none` per this repo's own convention -- app settings values
are echoed back in plaintext otherwise.)

## 5. Wait for the first export run

Daily-recurrence exports typically run within a few hours of creation,
then once daily after that. Check the container for output:

```bash
az storage blob list \
  --account-name "$STORAGE_NAME" \
  --container-name cost-exports \
  --auth-mode login \
  -o table
```

Once a CSV appears under `resource-costs/`, `_sync_cost_export_if_stale()`
will pick it up on the next cold-cache dashboard request and populate
`CostRecord` -- `_resource_costs_from_db()` and `_monthly_trend_from_db()`
take over from the live API automatically at that point, with the live
API + `_retry_on_429()` path remaining as a fallback if the DB has no
data for the requested period yet.
