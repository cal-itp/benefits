#!/usr/bin/env bash
set -eux

python manage.py dumpdata --exclude auth.permission --exclude contenttypes > unreviewed_fixtures.json
