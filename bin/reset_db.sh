#!/usr/bin/env bash
set -ex

# construct the path to the database file from environment or default
DB_DIR="${DJANGO_STORAGE_DIR:-.}"
DB_FILE="${DJANGO_DB_FILE:-django.db}"
DB_PATH="${DB_DIR}/${DB_FILE}"

if ! [[ -f "{$DB_PATH}" ]]; then
    # definitely reset if the database file is not found
    DB_RESET=true
else
    # use the DJANGO_DB_RESET env var or default to true
    DB_RESET="${DJANGO_DB_RESET:-true}"
fi

if [[ $DB_RESET = true ]]; then
    # delete existing DB, if present
    rm -f "${DB_PATH}"

    # run database migrations and other initialization
    bin/init.sh

    # create a superuser account for backend admin access
    # set username, email, and password using environment variables
    # DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, and DJANGO_SUPERUSER_PASSWORD
    python manage.py createsuperuser --no-input
else
    echo "DB_RESET is false, skipping"
fi

valid_fixtures=$(echo "$DJANGO_DB_FIXTURES" | grep -e fixtures\.json$ || test $? = 1)

if [[ -n "$valid_fixtures" ]]; then
    # load data fixtures
    python manage.py loaddata "$DJANGO_DB_FIXTURES"
else
    echo "No JSON fixtures to load"
fi
