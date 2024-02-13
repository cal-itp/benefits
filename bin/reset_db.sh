#!/usr/bin/env bash
set -eux

# remove database file

# construct the path to the database file from environment or default
DB_DIR="${DJANGO_DB_DIR:-.}"
DB_FILE="${DB_DIR}/django.db"

# -f forces the delete (and avoids an error when the file doesn't exist)
rm -f "${DB_FILE}"

# run database migrations and other initialization

bin/init.sh

# create a superuser account for backend admin access
# set username, email, and password using environment variables
# DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, and DJANGO_SUPERUSER_PASSWORD

python manage.py createsuperuser --no-input

# load sample data fixtures

python manage.py loaddata benefits/core/migrations/local_fixtures.json
