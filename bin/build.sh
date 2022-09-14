#!/usr/bin/env bash
set -eux

docker compose build client

docker compose build dev

docker compose pull server
