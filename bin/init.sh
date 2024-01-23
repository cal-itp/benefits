#!/usr/bin/env bash
set -eux

# run database migrations

python manage.py migrate

# generate language *.mo files for use by Django

python manage.py compilemessages

# collect static files

python manage.py collectstatic --no-input
