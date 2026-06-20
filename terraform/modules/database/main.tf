resource "azurerm_postgresql_flexible_server" "main" {
  name                   = "pg-${var.prefix}"
  location               = var.location
  resource_group_name    = var.resource_group_name
  version                = "16"
  administrator_login    = "djangoadmin"
  administrator_password = var.db_password
  storage_mb             = 32768
  sku_name               = "B_Standard_B1ms"
  backup_retention_days  = var.environment == "production" ? 14 : 7
  tags                   = var.tags

  private_dns_zone_id = var.pg_dns_zone_id
  delegated_subnet_id = var.data_subnet_id

  public_network_access_enabled = false
}

resource "azurerm_postgresql_flexible_server_database" "main" {
  name      = "djangodb"
  server_id = azurerm_postgresql_flexible_server.main.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}

resource "azurerm_postgresql_flexible_server_configuration" "pgaudit" {
  name      = "azure.extensions"
  server_id = azurerm_postgresql_flexible_server.main.id
  value     = "PGAUDIT"
}
