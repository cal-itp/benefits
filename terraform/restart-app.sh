#!/bin/bash

set -e

if [ $# -ne 1 ]; then
  echo "Usage: $0 D|T|P"
  exit 1
fi

ENV="$1"
APP="AS-CDT-PUB-VIP-CALITP-$ENV-001"
RG="RG-CDT-PUB-VIP-CALITP-$ENV-001"
NOW=$(date --utc)

az webapp config appsettings set --name "$APP" --resource-group "$RG" --settings change_me_to_refresh_secrets="$NOW"
