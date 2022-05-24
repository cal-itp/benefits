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
    ignore_changes = [
      tags,
    ]
  }
}
