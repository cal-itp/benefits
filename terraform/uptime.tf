module "dev_healthcheck" {
  source = "./uptime"

  action_group_id = azurerm_monitor_action_group.dev_email.id
  name                    = "dev-healthcheck"
  resource_group_name = data.azurerm_resource_group.benefits.name
  url = "https://dev-benefits.calitp.org/healthcheck"
}

# migrations

moved {
  from = azurerm_application_insights_web_test.dev_healthcheck
  to   = module.dev_healthcheck.azurerm_application_insights_web_test.healthcheck
}

moved {
  from = azurerm_monitor_metric_alert.uptime
  to = module.dev_healthcheck.azurerm_monitor_metric_alert.uptime
}
