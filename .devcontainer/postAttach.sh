#!/usr/bin/env bash
set -eu

# The global gitconfig gets copied into the container:
#
# https://code.visualstudio.com/docs/remote/containers#_sharing-git-credentials-with-your-container
#
# and may have a hooksPath setting that is incompatible with pre-commit.
#
# https://github.com/pre-commit/pre-commit/issues/1198#issuecomment-547478570
#
# Remove it if present.
git config --global --unset-all core.hooksPath

# initialize hook environments
pre-commit install --install-hooks --overwrite

# manage commit-msg hooks
pre-commit install --hook-type commit-msg

# install cypress
cd tests/cypress && npm install && npx cypress install
