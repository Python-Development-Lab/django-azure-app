output "db_host" {
  value = azurerm_postgresql_flexible_server.main.fqdn
}

output "db_name" {
  value = azurerm_postgresql_flexible_server_database.main.name
}

output "server_id" {
  value = azurerm_postgresql_flexible_server.main.id
}
