output "benefits_principal_id" {
  description = "The Principal ID of the Benefits Container App Managed Identity"
  value       = azurerm_container_app.benefits.identity[0].principal_id
}

output "pgadmin_principal_id" {
  description = "The Principal ID of the pgAdmin Container App Managed Identity"
  value       = azurerm_container_app.pgadmin.identity[0].principal_id
}
