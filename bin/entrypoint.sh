#!/usr/bin/env bash
set -e

# attempt to dispatch to some know sub-commands

cmd="$@"
sub="$1"
shift

case $sub in
    data) cmd="bin/data.sh" ;;
    manage) cmd="python manage.py" ;;
    migrate) cmd="bin/migrate.sh" ;;
    shell) cmd="python manage.py shell" ;;
    superuser) cmd="bin/superuser.sh" ;;
esac

exec $cmd "$@"
