#!/usr/bin/env bash
set -eux

# initialize Django

bin/init.sh

# start the web server

nginx

# start the application server

python -m gunicorn -c $GUNICORN_CONF benefits.wsgi
