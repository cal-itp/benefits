#!/usr/bin/env bash
set -eux

# container startup script specifically for running Cypress tests
# needs to reset the DB with sample data and then start the app normally

bin/reset_db.sh

bin/start.sh
