#!/usr/bin/env bash
set -e

# Run Django database migrations
python manage.py migrate admin zero && \
python manage.py migrate auth zero && \
python manage.py migrate core zero && \
python manage.py migrate