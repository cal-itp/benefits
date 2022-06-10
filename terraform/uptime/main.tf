resource "azurerm_application_insights_web_test" "healthcheck" {
  name                    = var.name
  location                = var.application_insights.location
  resource_group_name     = var.application_insights.resource_group_name
  application_insights_id = var.application_insights.id
  kind                    = "ping"
  enabled                 = true

  # "We strongly recommend testing from … a minimum of five locations."
  # https://docs.microsoft.com/en-us/azure/azure-monitor/app/monitor-web-app-availability#create-a-test
  geo_locations = [
    "us-fl-mia-edge", # Central US
    "us-va-ash-azr",  # East US
    "us-il-ch1-azr",  # North Central US
    "us-tx-sn1-azr",  # South Central US
    "us-ca-sjc-azr",  # West US
  ]

  configuration = templatefile("${path.module}/webtest.xml", { url = var.url })

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_monitor_metric_alert" "uptime" {
  name                = "uptime-${var.name}"
  resource_group_name = var.application_insights.resource_group_name
  scopes = [
    azurerm_application_insights_web_test.healthcheck.id,
    var.application_insights.id
  ]
  severity = var.severity

  application_insights_web_test_location_availability_criteria {
    web_test_id  = azurerm_application_insights_web_test.healthcheck.id
    component_id = var.application_insights.id
    # "the optimal configuration is to have the number of test locations be equal to the alert location threshold + 2"
    # https://docs.microsoft.com/en-us/azure/azure-monitor/app/monitor-web-app-availability#create-a-test
    failed_location_count = length(azurerm_application_insights_web_test.healthcheck.geo_locations) - 2
  }

  action {
    action_group_id = var.action_group_id
  }

  lifecycle {
    ignore_changes = [tags]
  }
}
