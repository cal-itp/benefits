resource "azurerm_log_analytics_workspace" "main" {
  name                = "CDT-OET-PUB-CALITP-${local.env_letter}-001"
  location            = data.azurerm_resource_group.prod.location
  resource_group_name = data.azurerm_resource_group.prod.name

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_application_insights" "dev" {
  name                = "aI-cdt-pub-vip-calitp-${lower(local.env_letter)}-001-dev"
  application_type    = "web"
  location            = data.azurerm_resource_group.prod.location
  resource_group_name = data.azurerm_resource_group.prod.name
  sampling_percentage = 0
  workspace_id        = azurerm_log_analytics_workspace.main.id

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_application_insights" "test" {
  name                = "AI-CDT-PUB-VIP-CALITP-${local.env_letter}-001-test"
  application_type    = "web"
  location            = data.azurerm_resource_group.prod.location
  resource_group_name = data.azurerm_resource_group.prod.name
  sampling_percentage = 0
  workspace_id        = azurerm_log_analytics_workspace.main.id

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_application_insights" "prod" {
  name                = "AI-CDT-PUB-VIP-CALITP-${local.env_letter}-001"
  application_type    = "web"
  location            = data.azurerm_resource_group.prod.location
  resource_group_name = data.azurerm_resource_group.prod.name
  sampling_percentage = 0
  workspace_id        = azurerm_log_analytics_workspace.main.id

  lifecycle {
    ignore_changes = [tags]
  }
}

# created manually
# https://slack.com/help/articles/206819278-Send-emails-to-Slack
data "azurerm_key_vault_secret" "slack_benefits_notify_email" {
  name         = "slack-benefits-notify-email"
  key_vault_id = azurerm_key_vault.main.id
}

resource "azurerm_monitor_action_group" "eng_email" {
  name                = "benefits-notify Slack channel email"
  resource_group_name = data.azurerm_resource_group.prod.name
  short_name          = "slack-notify"

  email_receiver {
    name          = "Benefits engineering team"
    email_address = data.azurerm_key_vault_secret.slack_benefits_notify_email.value
  }

  lifecycle {
    ignore_changes = [tags]
  }
}

# migrations

moved {
  from = azurerm_monitor_action_group.dev_email
  to   = azurerm_monitor_action_group.eng_email
}
