#!/usr/bin/env bash
set -eux

# remove existing (old) database file
# -f forces the delete (and avoids an error when the file doesn't exist)

rm -f django.db

# run database migrations

if [[ ${DJANGO_LOAD_SAMPLE_DATA:-true} = false ]]; then
    if [[ -d ${DJANGO_MIGRATIONS_DIR:-false} ]]; then
        cp ${DJANGO_MIGRATIONS_DIR}/0002_*.py ./benefits/core/migrations/
    else
        echo "DJANGO_MIGRATIONS_DIR is either unset or not a directory"
    fi
fi

python manage.py migrate

# create a superuser account for backend admin access
# check DJANGO_ADMIN = true, default to false if empty or unset

if [[ ${DJANGO_ADMIN:-false} = true ]]; then
    python manage.py createsuperuser
else
    echo "superuser: Django not configured for Admin access"
fi

# generate language *.mo files for use by Django

python manage.py compilemessages

# collect static files

python manage.py collectstatic --no-input
