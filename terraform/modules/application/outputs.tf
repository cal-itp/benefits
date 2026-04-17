output "web_principal_id" {
  description = "The Principal ID of the Benefits (web) Container App Managed Identity"
  value       = azurerm_container_app.web.identity[0].principal_id
}

output "pgadmin_principal_id" {
  description = "The Principal ID of the pgAdmin Container App Managed Identity"
  value       = azurerm_container_app.pgadmin.identity[0].principal_id
}
