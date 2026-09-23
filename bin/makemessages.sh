#!/usr/bin/env bash
set -eu

# generate initial .PO files from msgids in template and view files

# process Benefits using the -i flag to ignore the MMW directory
# this ensures strings from MMW do not leak into Benefits' message files
python manage.py makemessages -a --no-obsolete --no-location --ignore="benefits/metro_mobility_wallet/*"
# to enforce only processing MMW messages navigate into the app directory and use django-admin makemessages
# Django restricts its scan to this folder and outputs the translations directly to benefits/metro_mobility_wallet/locale/
# https://docs.djangoproject.com/en/6.1/topics/i18n/translation/#message-files
cd benefits/metro_mobility_wallet
django-admin makemessages -a  --no-obsolete --no-location
cd ../..

# put back bug-report link

# for Benefits
sed -i 's/Report-Msgid-Bugs-To\:/Report-Msgid-Bugs-To\: https\:\/\/github.com\/cal-itp\/benefits\/issues/g' benefits/locale/*/*/*.po
# for MMW
sed -i 's/Report-Msgid-Bugs-To\:/Report-Msgid-Bugs-To\: https\:\/\/github.com\/cal-itp\/benefits\/issues/g' benefits/metro_mobility_wallet/locale/*/*/*.po
