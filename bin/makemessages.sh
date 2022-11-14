#!/usr/bin/env bash
set -eu

# generate initial .PO files from msgids in template and view files

python manage.py makemessages -a --no-obsolete --no-location

# put back bug-report link

sed -i 's/Report-Msgid-Bugs-To\:/Report-Msgid-Bugs-To\: https\:\/\/github.com\/cal-itp\/benefits\/issues/g' benefits/locale/*/*/*.po
