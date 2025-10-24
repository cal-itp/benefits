#!/bin/bash

set -e


ENV=$1

if [ $# -ne 1 ]; then
  echo "Usage: $0 <env>"
  exit 1
fi

printf "\n\nSelecting the Terraform workspace...\n"
if [ "$ENV" = "prod" ]; then
  terraform workspace select default
  SUBSCRIPTION="CDT/ODI Production"
else
  terraform workspace select "$ENV"
  SUBSCRIPTION="CDT/ODI Development"
fi

printf "Intializing Terraform...\n\n"
# automatically inject the subscription ID
PROD_ID=$(az account list --query "[?name == '$SUBSCRIPTION'] | [0].id" --output tsv)
terraform init -backend-config="subscription_id=$PROD_ID"


echo "Setting the subscription for the Azure CLI..."
az account set --subscription="$SUBSCRIPTION"

echo "Done!"
