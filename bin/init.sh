#!/usr/bin/env bash
set -eu

# run database migrations

python manage.py migrate

# load config data

# check if init json data provided
# if so write to temp file and load from there
if [[ -v DJANGO_INIT_JSON ]] && [[ ! -z "$DJANGO_INIT_JSON" ]]; then
    echo $DJANGO_INIT_JSON > /tmp/data.json
    DJANGO_INIT_PATH=/tmp/data.json
fi

python manage.py loaddata $DJANGO_INIT_PATH

# create a superuser account for backend admin access
# check DJANGO_ADMIN = true, default to false if empty or unset

if [[ ${DJANGO_ADMIN:-false} = true ]]; then
    python manage.py createsuperuser
else
    echo "superuser: Django not configured for Admin access"
fi