#!/usr/bin/env bash
set -eu

# run database migrations

python manage.py migrate

# load config data

python manage.py loaddata $DJANGO_INIT_PATH

# create a superuser account for backend admin access
# check DJANGO_ADMIN = true, default to false if empty or unset

if [[ ${DJANGO_ADMIN:-false} = true ]]; then
    python manage.py createsuperuser
else
    echo "superuser: Django not configured for Admin access"
fi

# generate language *.mo files for use by Django

django-admin compilemessages

# collect static files

python manage.py collectstatic --no-input
