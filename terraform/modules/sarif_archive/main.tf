resource "azurerm_storage_account" "sarif" {
  name                            = "stdjangosarif89420"
  resource_group_name             = var.resource_group_name
  location                        = var.location
  account_tier                    = "Standard"
  account_replication_type        = "LRS"
  account_kind                    = "StorageV2"
  min_tls_version                 = "TLS1_2"
  https_traffic_only_enabled      = true
  allow_nested_items_to_be_public = false
  tags                             = var.tags
}

resource "azurerm_storage_container" "sarif_archive" {
  name                  = "sarif-archive"
  storage_account_name  = azurerm_storage_account.sarif.name
  container_access_type = "private"
}

resource "azurerm_role_assignment" "cicd_blob_contributor" {
  scope                = azurerm_storage_account.sarif.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = var.cicd_principal_id
}
