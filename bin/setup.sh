#!/usr/bin/env bash
set -ex

 # Ensure databases, users, migrations, and superuser are set up
should_reset=${REMOTE_CONTAINERS:-false}
if [[ $should_reset == "true" ]]; then
    # running in a devcontainer, reset the DB
    python manage.py ensure_db --reset
else
    python manage.py ensure_db
fi

valid_fixtures=$(echo "$DJANGO_DB_FIXTURES" | grep -e fixtures\.json$ || test $? = 1)

if [[ -n "$valid_fixtures" ]]; then
    # load data fixtures
    python manage.py loaddata "$DJANGO_DB_FIXTURES"
else
    echo "No JSON fixtures to load"
fi
