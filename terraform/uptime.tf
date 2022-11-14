module "dev_healthcheck" {
  source = "./uptime"

  action_group_id      = azurerm_monitor_action_group.eng_email.id
  application_insights = azurerm_application_insights.prod
  name                 = "dev-healthcheck"
  url                  = "https://dev-benefits.calitp.org/healthcheck"
}

module "test_healthcheck" {
  source = "./uptime"

  action_group_id      = azurerm_monitor_action_group.eng_email.id
  application_insights = azurerm_application_insights.prod
  name                 = "test-healthcheck"
  url                  = "https://test-benefits.calitp.org/healthcheck"
}

module "prod_healthcheck" {
  source = "./uptime"

  action_group_id      = azurerm_monitor_action_group.eng_email.id
  application_insights = azurerm_application_insights.prod
  name                 = "prod-healthcheck"
  url                  = "https://benefits.calitp.org/healthcheck"
}

# migrations

moved {
  from = azurerm_application_insights_web_test.dev_healthcheck
  to   = module.dev_healthcheck.azurerm_application_insights_web_test.healthcheck
}

moved {
  from = azurerm_monitor_metric_alert.uptime
  to   = module.dev_healthcheck.azurerm_monitor_metric_alert.uptime
}
