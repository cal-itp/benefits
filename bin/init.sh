#!/usr/bin/env bash
set -eux

# run database migrations

benefits migrate

# generate language *.mo files for use by Django

benefits compilemessages

# collect static files

benefits collectstatic --no-input
