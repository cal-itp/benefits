locals {
  communication_service_name                 = "ACS-CDT-PUB-VIP-CALITP-${local.env_letter}-001"
  data_location                              = "United States"
  custom_domain_name                         = "benefits.calitp.org"
  azure_communication_connection_string_name = "azure-communication-connection-string"
  azure_communication_from_email_name        = "azure-communication-from-email"
  # Determine the correct sender domain based on the environment.
  # If is_prod is true, use the custom domain; otherwise, use the Azure-managed domain.
  sender_domain = local.is_prod ? azurerm_email_communication_service_domain.custom[0].mail_from_sender_domain : azurerm_email_communication_service_domain.azure_managed[0].mail_from_sender_domain
  sender_email = "DoNotReply@${local.sender_domain}"
}

resource "azurerm_key_vault_secret" "azure_communication_connection_string" {
  name         = local.azure_communication_connection_string_name
  value        = azurerm_communication_service.main.primary_connection_string
  key_vault_id = azurerm_key_vault.main.id
  content_type = "password"
}

resource "azurerm_key_vault_secret" "azure_communication_from_email" {
  name         = local.azure_communication_from_email_name
  value        = local.sender_email
  key_vault_id = azurerm_key_vault.main.id

  # This resource depends on the creation of one of the two possible domains.
  depends_on = [
    azurerm_email_communication_service_domain.azure_managed[0],
    azurerm_email_communication_service_domain.custom[0]
  ]
}

resource "azurerm_communication_service" "main" {
  name                = local.communication_service_name
  resource_group_name = data.azurerm_resource_group.main.name
  data_location       = local.data_location

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_email_communication_service" "main" {
  name                = local.communication_service_name
  resource_group_name = data.azurerm_resource_group.main.name
  data_location       = local.data_location

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_email_communication_service_domain" "azure_managed" {
  count = local.is_prod ? 0 : 1

  # when domain_management="AzureManaged",
  # the name has to be "AzureManagedDomain"
  # https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/email_communication_service_domain#name-19
  name                             = "AzureManagedDomain"
  email_service_id                 = azurerm_email_communication_service.main.id
  domain_management                = "AzureManaged"
  user_engagement_tracking_enabled = true

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_communication_service_email_domain_association" "azure_managed" {
  count = local.is_prod ? 0 : 1

  communication_service_id = azurerm_communication_service.main.id
  email_service_domain_id  = azurerm_email_communication_service_domain.azure_managed[0].id
}

# This domain is only created when local.is_prod is true.
resource "azurerm_email_communication_service_domain" "custom" {
  count = local.is_prod ? 1 : 0

  name                             = local.custom_domain_name
  email_service_id                 = azurerm_email_communication_service.main.id
  domain_management                = "CustomerManaged"
  user_engagement_tracking_enabled = true

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_communication_service_email_domain_association" "custom" {
  count = local.is_prod ? 1 : 0

  communication_service_id = azurerm_communication_service.main.id
  email_service_domain_id  = azurerm_email_communication_service_domain.custom[0].id
}
