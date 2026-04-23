#!/usr/bin/env bash
set -ex

# Uninstall all existing packages
pip freeze --exclude-editable | xargs pip uninstall -y

# Reinstall from list of direct dependencies
pip install --user -r requirements.in

# Update requirements.txt with new list of intalled packages (excluding benefits itself)
pip freeze --exclude-editable > requirements.txt

# Re-add header to top of requirements.txt
tmpfile=$(mktemp)
cp requirements.txt "$tmpfile" &&
cat - "$tmpfile" <<HEADER >requirements.txt
# List of all dependencies, direct and transitive
# Consumed by tool.setuptools.dynamic.dependencies in pyproject.toml
# DO NOT EDIT DIRECTLY! Update with bin/dependencies.sh
HEADER
rm "$tmpfile"

# Reinstall dev/test/docs dependencies, in case this container continues to be used
pip install --user -e .[dev,test]
pip install --user -r docs/requirements.txt
