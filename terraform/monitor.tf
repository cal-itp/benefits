data "azurerm_key_vault" "main" {
  name                = "KV-CDT-PUB-CALITP-P-001"
  resource_group_name = data.azurerm_resource_group.benefits.name
}

# created manually
# https://slack.com/help/articles/206819278-Send-emails-to-Slack
data "azurerm_key_vault_secret" "slack_benefits_notify_email" {
  name         = "slack-benefits-notify-email"
  key_vault_id = data.azurerm_key_vault.main.id
}

resource "azurerm_monitor_action_group" "dev_email" {
  name                = "benefits-notify Slack channel email"
  resource_group_name = data.azurerm_resource_group.benefits.name
  short_name          = "slack-notify"

  email_receiver {
    name          = "Benefits engineering team"
    email_address = data.azurerm_key_vault_secret.slack_benefits_notify_email.value
  }

  lifecycle {
    ignore_changes = [tags]
  }
}
