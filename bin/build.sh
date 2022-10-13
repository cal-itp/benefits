#!/usr/bin/env bash
set -eux

# if on Apple M1
# https://stackoverflow.com/a/65259353/358804
if [[ $(uname -m) == 'arm64' ]]; then
    # workaround for an issue in BuildKit causing dependent builds (specifically the dev image) to fail
    # https://github.com/docker/compose/issues/8449#issuecomment-1125761231
    export DOCKER_BUILDKIT=0
fi

docker compose build --pull client

docker compose build dev

docker compose pull server
