resource "azurerm_service_plan" "main" {
  name                = "plan-${var.prefix}"
  location            = var.location
  resource_group_name = var.resource_group_name
  os_type             = "Linux"
  sku_name            = var.environment == "production" ? "S1" : "B1"
  tags                = var.tags
}

resource "azurerm_linux_web_app" "main" {
  name                = "app-${var.prefix}"
  location            = var.location
  resource_group_name = var.resource_group_name
  service_plan_id     = azurerm_service_plan.main.id
  tags                = var.tags

  site_config {
    always_on = var.environment == "production"

    application_stack {
      python_version = "3.12"
    }
  }

  app_settings = {
    "WEBSITE_RUN_FROM_PACKAGE"       = "1"
    "SCM_DO_BUILD_DURING_DEPLOYMENT" = "true"
    "BUILDING"                       = "false"
    "DEBUG"                          = var.environment == "production" ? "False" : "True"
    "ALLOWED_HOSTS"                  = "app-${var.prefix}.azurewebsites.net,localhost"
    "AZURE_KEY_VAULT_NAME"           = var.key_vault_uri
    "OTEL_SERVICE_NAME"              = "django-${var.environment}"
    "DB_HOST"                        = var.db_host
    "DB_NAME"                        = var.db_name
  }

  identity {
    type = "SystemAssigned"
  }

  virtual_network_subnet_id = var.app_subnet_id
}

resource "azurerm_linux_web_app_slot" "staging" {
  count          = var.environment == "production" ? 1 : 0
  name           = "staging"
  app_service_id = azurerm_linux_web_app.main.id

  site_config {
    always_on = false
    application_stack {
      python_version = "3.12"
    }
  }

  identity {
    type = "SystemAssigned"
  }

  app_settings = {
    "BUILDING" = "true"
  }
}

resource "azurerm_role_assignment" "app_kv_secrets_user" {
  scope                = var.key_vault_id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_linux_web_app.main.identity[0].principal_id
}
