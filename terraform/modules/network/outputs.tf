output "vnet_id" {
  value = azurerm_virtual_network.main.id
}

output "app_subnet_id" {
  value = azurerm_subnet.app.id
}

output "data_subnet_id" {
  value = azurerm_subnet.data.id
}

output "kv_dns_zone_id" {
  value = azurerm_private_dns_zone.kv.id
}

output "pg_dns_zone_id" {
  value = azurerm_private_dns_zone.pg.id
}

output "kv_dns_zone_name" {
  value = azurerm_private_dns_zone.kv.name
}

output "pg_dns_zone_name" {
  value = azurerm_private_dns_zone.pg.name
}
