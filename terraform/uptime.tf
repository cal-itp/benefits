data "azurerm_application_insights" "benefits" {
  name                = "AS-CDT-CALITP-D-001"
  resource_group_name = data.azurerm_resource_group.benefits.name
}


resource "azurerm_application_insights_web_test" "dev_healthcheck" {
  name                    = "dev-healthcheck"
  location                = data.azurerm_application_insights.benefits.location
  resource_group_name     = data.azurerm_resource_group.benefits.name
  application_insights_id = data.azurerm_application_insights.benefits.id
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

  configuration = <<XML
<WebTest Name="dev-healthcheck" Enabled="True" CssProjectStructure="" CssIteration="" Timeout="120" WorkItemIds=""
  xmlns="http://microsoft.com/schemas/VisualStudio/TeamTest/2010" Description="" CredentialUserName="" CredentialPassword="" PreAuthenticate="True" Proxy="default" StopOnError="False" RecordedResultFile="" ResultsLocale="">
  <Items>
    <Request Method="GET" Version="1.1" Url="https://dev-benefits.calitp.org/healthcheck" ThinkTime="0" Timeout="300" ParseDependentRequests="True" FollowRedirects="True" RecordResult="True" Cache="False" ResponseTimeGoal="0" Encoding="utf-8" ExpectedHttpStatusCode="200" ExpectedResponseUrl="" ReportingName="" IgnoreHttpStatusCode="False" />
  </Items>
</WebTest>
XML

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_monitor_metric_alert" "uptime" {
  name                = "uptime"
  resource_group_name = data.azurerm_resource_group.benefits.name
  scopes = [
    azurerm_application_insights_web_test.dev_healthcheck.id,
    data.azurerm_application_insights.benefits.id
  ]
  severity = 1

  application_insights_web_test_location_availability_criteria {
    web_test_id           = azurerm_application_insights_web_test.dev_healthcheck.id
    component_id          = data.azurerm_application_insights.benefits.id
    # "the optimal configuration is to have the number of test locations be equal to the alert location threshold + 2"
    # https://docs.microsoft.com/en-us/azure/azure-monitor/app/monitor-web-app-availability#create-a-test
    failed_location_count = length(azurerm_application_insights_web_test.dev_healthcheck.geo_locations) - 2
  }

  action {
    action_group_id = azurerm_monitor_action_group.dev_email.id
  }

  lifecycle {
    ignore_changes = [tags]
  }
}
