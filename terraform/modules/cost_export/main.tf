# Deliberate extension from 6 to 7 Terraform modules (network, key_vault,
# database, app_service, monitoring, sarif_archive + this one). The repo
# constitution's "6-module structure" describes the state as of its last
# update, not a hard ceiling -- a 7th module for a genuinely separate
# concern (Cost Management Export storage) is preferable to overloading
# an existing module with unrelated resources. Flagged here explicitly
# per AI PR Review feedback so this isn't silent drift.

variable "location" {
  type    = string
  default = "westeurope"
}

variable "resource_group_name" {
  type = string
}

variable "tags" {
  type    = map(string)
  default = {}
}

variable "app_service_msi_principal_id" {
  type        = string
  description = "Principal ID of the App Service's System-Assigned Managed Identity (needs Storage Blob Data Reader on the export container)."
}

# Storage Account names must be globally unique, lowercase alphanumeric
# only, 3-24 chars -- cannot safely derive from var.prefix (may contain
# hyphens / exceed length). Mirrors the existing random-suffix pattern
# already used for the Terraform state storage account in this project
# (stdjangotfstate35607).
resource "random_string" "cost_export_suffix" {
  length  = 6
  special = false
  upper   = false
}

resource "azurerm_storage_account" "cost_export" {
  name                     = "stcostexp${random_string.cost_export_suffix.result}"
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS" # cheapest tier -- CSV exports are tiny, no redundancy needed
  min_tls_version          = "TLS1_2"
  tags                     = var.tags
}

resource "azurerm_storage_container" "cost_export" {
  name                  = "cost-exports"
  storage_account_name  = azurerm_storage_account.cost_export.name
  container_access_type = "private"
}

# The Cost Management Export resource itself (created via `az costmanagement
# export create`, not this module -- see docs/cost-export-setup.md). Its
# System-Assigned Identity needs write access to this storage account. This
# role assignment is created here, scoped by principal_id passed in as a
# variable once the export exists (chicken-and-egg: the export's identity
# principal_id is only known after `az costmanagement export create` runs).
variable "cost_export_identity_principal_id" {
  type        = string
  default     = ""
  description = "Principal ID of the Cost Management Export's System-Assigned Identity. Leave empty until the export is created via the CLI step in docs/cost-export-setup.md, then set this and re-apply."
}

resource "azurerm_role_assignment" "export_writer" {
  count = var.cost_export_identity_principal_id != "" ? 1 : 0
  # Scoped to the container, not the whole storage account: least-privilege
  # per AI PR Review feedback -- there is currently only one container in
  # this account, but scoping to the account would implicitly grant access
  # to any container added here in the future. Falls back to account-level
  # scope (see git history) if this repo's pinned azurerm provider version
  # doesn't expose resource_manager_id on azurerm_storage_container.
  #
  # Role choice: Storage Blob Data Contributor (not just Reader/Writer)
  # includes delete permission on blobs in this container. No narrower
  # built-in Azure role exists for "write and overwrite, but never
  # delete" blob access. Accepted deliberately: this identity is used
  # exclusively by the Cost Management export job, which overwrites the
  # same MonthToDate CSV path on each daily run -- delete capability is
  # inherent to that overwrite semantics, not incidental over-grant.
  scope                = azurerm_storage_container.cost_export.resource_manager_id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = var.cost_export_identity_principal_id
}

resource "azurerm_role_assignment" "app_reader" {
  scope                = azurerm_storage_container.cost_export.resource_manager_id
  role_definition_name = "Storage Blob Data Reader"
  principal_id         = var.app_service_msi_principal_id
}

output "storage_account_name" {
  value = azurerm_storage_account.cost_export.name
}

output "container_name" {
  value = azurerm_storage_container.cost_export.name
}
