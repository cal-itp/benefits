#!/usr/bin/env bash
set -eux

# generate language *.mo files for use by Django

python manage.py compilemessages

# collect static files

python manage.py collectstatic --no-input

# start the web server

nginx

# start the application server

python -m gunicorn -c $GUNICORN_CONF benefits.wsgi
