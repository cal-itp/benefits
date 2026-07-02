#!/usr/bin/env bash
set -ex

# Uninstall benefits individually because `pip uninstall` chokes on how it's formatted in `pip freeze` output
pip uninstall -y benefits

# Uninstall everything else
pip freeze | xargs pip uninstall -y

# Update pylock.toml
pip lock .

# TEMP: Extract local benefits package from the lockfile
# See https://github.com/pypa/pip/issues/13952#issuecomment-4357746894 and the immediate reply to it
# TODO: Remove once that is resolved
export SEARCH_STRING='[[packages]]
name = "benefits"

[packages.directory]
path = "."'
# Doing this via Python because it's very hard to do with Bash alone
python -c 'import sys, os; f=sys.argv[1]; c=open(f).read(); open(f, "w").write(c.replace(os.environ["SEARCH_STRING"], ""))' pylock.toml

# Install the dependencies from the lockfile
pip install -r pylock.toml

# Reinstall dev/test/docs dependencies, in case this container continues to be used
pip install --user --group dev --group test -r docs/requirements.txt
