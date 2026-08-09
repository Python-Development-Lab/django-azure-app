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
  count                = var.cost_export_identity_principal_id != "" ? 1 : 0
  scope                = azurerm_storage_account.cost_export.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = var.cost_export_identity_principal_id
}

resource "azurerm_role_assignment" "app_reader" {
  scope                = azurerm_storage_account.cost_export.id
  role_definition_name = "Storage Blob Data Reader"
  principal_id         = var.app_service_msi_principal_id
}

output "storage_account_name" {
  value = azurerm_storage_account.cost_export.name
}

output "container_name" {
  value = azurerm_storage_container.cost_export.name
}
