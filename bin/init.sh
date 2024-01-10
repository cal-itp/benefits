#!/usr/bin/env bash
set -eux

# make the path to the database file from environment or default
DB_DIR="${DJANGO_DB_DIR:-.}"
DB_FILE="${DB_DIR}/django.db"
DB_RESET="${DJANGO_DB_RESET:-true}"

# remove existing (old) database file
if [[ $DB_RESET = true && -f $DB_FILE ]]; then
    # rename then delete the new file
    # trying to avoid a file lock on the existing file
    # after marking it for deletion
    mv "${DB_FILE}" "${DB_FILE}.old"
    rm "${DB_FILE}.old"
fi

# run database migrations

python manage.py migrate

# create a superuser account for backend admin access
# check DJANGO_ADMIN = true, default to false if empty or unset

if [[ ${DJANGO_ADMIN:-false} = true ]]; then
    cat benefits/superuser.py | python manage.py shell
else
    echo "superuser: Django not configured for Admin access"
fi

# generate language *.mo files for use by Django

python manage.py compilemessages

# collect static files

python manage.py collectstatic --no-input
