#!/usr/bin/env bash
set -eu

# ensure script runs from correct location

cd /home/calitp/app

# generate initial .PO files from msgids in template and view files

python manage.py makemessages -a --no-obsolete

# put back bug-report link

sed -i 's/Report-Msgid-Bugs-To\:/Report-Msgid-Bugs-To\: https\:\/\/github.com\/cal-itp\/benefits\/issues/g' benefits/locale/**/**/**.po

# loop over each language's fixture_messages directory for each language and append to main file
for path in ./benefits/locale/*; do
    [ -d "${path}" ] || continue # if not a directory, skip

    echo "Processing fixture messages for ${path}"
    main_file=$path/LC_MESSAGES/django.po
    echo "" >> $main_file
    echo "# Fixture messages - entries below are copied from files in this language's fixture_messages directory." >> $main_file
    echo "# !! Any edits you make here will be overwritten when bin/makemessages.sh is run. !!" >> $main_file

    for file in $path/fixture_messages/*; do
        echo "Writing ${file} to django.po"
        echo "" >> $main_file
        echo "# Copied from ${file}" >> $main_file
        cat $file >> $main_file
    done
done
