#!/bin/bash

set -e


ENV=$1


printf "Intializing Terraform...\n\n"
# automatically inject the subscription ID
PROD_ID=$(az account list --query "[?name == 'CDT/ODI Production'] | [0].id" --output tsv)
terraform init -backend-config="subscription_id=$PROD_ID"

printf "\n\nSelecting the Terraform workspace...\n"
if [ "$ENV" = "prod" ]; then
  terraform workspace select default
  SUBSCRIPTION="CDT/ODI Production"
else
  terraform workspace select "$ENV"
  SUBSCRIPTION="CDT/ODI Development"
fi

echo "Setting the subscription for the Azure CLI..."
az account set --subscription="$SUBSCRIPTION"

echo "Done!"
