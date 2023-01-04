module "healthcheck" {
  source = "./uptime"

  action_group_id      = azurerm_monitor_action_group.eng_email.id
  application_insights = azurerm_application_insights.main
  # not strictly necessary to include the environment name, but helps to make the alerts more clear
  name = "${local.env_name}-healthcheck"
  url  = "https://${local.hostname}/healthcheck"
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

moved {
  from = module.prod_healthcheck
  to   = module.healthcheck
}
