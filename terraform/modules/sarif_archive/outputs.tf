output "storage_account_name" {
  value = azurerm_storage_account.sarif.name
}

output "container_name" {
  value = azurerm_storage_container.sarif_archive.name
}
