#!/bin/bash

set -e


ENV=$1

if [ $# -ne 1 ]; then
  echo "Usage: $0 <env>"
  exit 1
fi

SUBSCRIPTION_NAME="CDT/ODI Production"
SUBSCRIPTION_ID=$(az account list --query "[?name == '$SUBSCRIPTION_NAME'] | [0].id" --output tsv)

# ensure that the correct subscription is active before running terraform commands
echo "Setting the subscription for the Azure CLI..."
az account set --subscription="$SUBSCRIPTION_NAME"

printf "Intializing Terraform...\n\n"
terraform init -backend-config="subscription_id=$SUBSCRIPTION_ID"

printf "Selecting the Terraform workspace...\n"
if [ "$ENV" = "prod" ]; then
  terraform workspace select default
else
  terraform workspace select "$ENV"
fi

echo "Done!"
