#!/usr/bin/env bash
set -eu

# To only process message files in metro_mobility_wallet, set working directory to the folder containing this script
# https://docs.djangoproject.com/en/6.1/ref/django-admin/#makemessages
cd "$(dirname "$0")"

# generate .PO files from msgids in template and view files
python ../../manage.py makemessages -a  --no-obsolete --no-location

# Apply bug-report link fix strictly to metro_mobility_wallet's locale files
sed -i 's/Report-Msgid-Bugs-To\:/Report-Msgid-Bugs-To\: https\:\/\/github.com\/cal-itp\/benefits\/issues/g' locale/*/*/*.po
