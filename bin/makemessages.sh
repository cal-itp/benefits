#!/usr/bin/env bash
set -eu

# ensure script runs from correct location

cd /home/calitp/app

# generate initial .PO files from msgids in template and view files

python manage.py makemessages -a --no-obsolete

# put back bug-report link

sed -i 's/Report-Msgid-Bugs-To\:/Report-Msgid-Bugs-To\: https\:\/\/github.com\/cal-itp\/benefits\/issues/g' benefits/locale/**/**/**.po
