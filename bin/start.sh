#!/usr/bin/env bash
set -eu

# initialize Django

bin/init.sh

# collect static files

python manage.py collectstatic --no-input

# start the web server

nginx

# start the application server

gunicorn benefits.wsgi:application