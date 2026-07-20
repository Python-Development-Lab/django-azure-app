data "azurerm_client_config" "current" {}

resource "azurerm_key_vault" "main" {
  name                      = "kv-${var.prefix}"
  location                  = var.location
  resource_group_name       = var.resource_group_name
  tenant_id                 = var.tenant_id
  sku_name                  = "standard"
  enable_rbac_authorization = true
  #tfsec:ignore:azure-keyvault-specify-network-acl
  purge_protection_enabled   = false #tfsec:ignore:azure-keyvault-no-purge
  soft_delete_retention_days = 7
  tags                       = var.tags
}

resource "azurerm_private_endpoint" "kv" {
  name                = "pe-kv-${var.prefix}"
  location            = var.location
  resource_group_name = var.resource_group_name
  subnet_id           = var.data_subnet_id
  tags                = var.tags

  private_service_connection {
    name                           = "kv-connection"
    private_connection_resource_id = azurerm_key_vault.main.id
    subresource_names              = ["vault"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "kv-dns-group"
    private_dns_zone_ids = [var.kv_dns_zone_id]
  }
}

resource "azurerm_key_vault_secret" "django_secret_key" {
  name         = "DJANGO-SECRET-KEY"
  value        = var.django_secret_key
  content_type = "text/plain"
  key_vault_id = azurerm_key_vault.main.id
  depends_on   = [azurerm_role_assignment.terraform_admin] #tfsec:ignore:azure-keyvault-ensure-secret-expiry
}

resource "azurerm_key_vault_secret" "azure_client_id" {
  name         = "AZURE-CLIENT-ID"
  value        = var.azure_client_id
  content_type = "text/plain" #tfsec:ignore:azure-keyvault-ensure-secret-expiry
  key_vault_id = azurerm_key_vault.main.id
  depends_on   = [azurerm_role_assignment.terraform_admin]
}

resource "azurerm_key_vault_secret" "azure_client_secret" {
  name         = "AZURE-CLIENT-SECRET"
  value        = var.azure_client_secret
  content_type = "text/plain" #tfsec:ignore:azure-keyvault-ensure-secret-expiry
  key_vault_id = azurerm_key_vault.main.id
  depends_on   = [azurerm_role_assignment.terraform_admin]
}

resource "azurerm_key_vault_secret" "azure_tenant_id" {
  name         = "AZURE-TENANT-ID"
  value        = var.tenant_id
  content_type = "text/plain" #tfsec:ignore:azure-keyvault-ensure-secret-expiry
  key_vault_id = azurerm_key_vault.main.id
  depends_on   = [azurerm_role_assignment.terraform_admin]
}

resource "azurerm_role_assignment" "terraform_admin" {
  scope                = azurerm_key_vault.main.id
  role_definition_name = "Key Vault Administrator"
  principal_id         = var.terraform_object_id
}

# Separate, independent role assignment for a human operator (e.g. project owner).
# Kept apart from terraform_admin so that CI/CD service principal rotation
# (var.terraform_object_id) never revokes a human's manual access, and vice versa.
resource "azurerm_role_assignment" "human_admin" {
  count                = var.human_admin_object_id != "" ? 1 : 0
  scope                = azurerm_key_vault.main.id
  role_definition_name = "Key Vault Administrator"
  principal_id         = var.human_admin_object_id
}
