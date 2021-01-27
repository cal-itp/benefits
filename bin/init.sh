#!/usr/bin/env bash
set -eu

# run database migrations

python manage.py migrate

# load model data

python manage.py loaddata data/client/*.json

# create a superuser account for backend admin access
# check DJANGO_ADMIN = true, default to false if empty or unset

if [ "${DJANGO_ADMIN:+false}" = true ] ; then
    python manage.py createsuperuser
else
    echo "superuser: Django not configured for Admin access"
fi