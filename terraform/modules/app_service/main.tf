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
    always_on              = var.environment == "production"
    vnet_route_all_enabled = true
    app_command_line       = "bash /home/site/wwwroot/startup.sh"

    application_stack {
      python_version = "3.12"
    }
  }

  app_settings = {
    "WEBSITE_RUN_FROM_PACKAGE"       = "0"
    "SCM_DO_BUILD_DURING_DEPLOYMENT" = "false"
    "BUILDING"                       = "false"
    "DEBUG"                          = "False"
    "ALLOWED_HOSTS"                  = "app-${var.prefix}.azurewebsites.net,localhost"
    "AZURE_KEY_VAULT_NAME"           = var.key_vault_uri
    "OTEL_SERVICE_NAME"              = "django-${var.environment}"
    "DB_HOST"                        = var.db_host
    "DB_NAME"                        = var.db_name
    "DB_USER"                        = var.db_user
    "DB_PASSWORD"                    = var.db_password
    "AZURE_CLIENT_ID"                = var.azure_client_id
    "AZURE_CLIENT_SECRET"            = var.azure_client_secret
    "AZURE_TENANT_ID"                = var.azure_tenant_id
    "SECRET_KEY"                     = var.django_secret_key
    "AZURE_REDIRECT_URI"             = var.azure_redirect_uri
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
