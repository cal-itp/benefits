#!/usr/bin/env bash

env=$1
secret_name=$2
secret_value=$3

if [ $# -ne 3 ]; then
  echo "Usage: $0 <D|T|P> <secret_name> <secret_value>"
  exit 1
fi

az keyvault secret set --vault-name "KV-CDT-PUB-CALITP-$env-001" --name $1 --value "$2"
