#!/usr/bin/env bash
set -eu

pytest --cov=benefits --cov-branch

coverage html --directory benefits/static/coverage

echo
echo "Launch the app and visit http://localhost:${DJANGO_LOCAL_PORT}/static/coverage/index.html"
