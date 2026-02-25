#!/usr/bin/env bash
set -eu

# Let the user know what fixtures they're pointed at currently.
echo -e "Using fixtures from: $DJANGO_DB_FIXTURES \n"

# Prompt the user to checkout the commit where those fixtures work.
read -p "Enter the commit on main just prior to model changes: " pre_model_change_commit

# Checkout that commit and reset the database.
git checkout $pre_model_change_commit
./bin/reset_db.sh

# Prompt the user to checkout the commit with the new model changes.
read -p "Enter the commit with the new model changes: " post_model_change_commit

# Checkout that commit and run migrations.
git checkout $post_model_change_commit
./bin/init.sh

# Export migrated fixtures and prompt user to review migrated contents.
temp_file_name="unreviewed_fixtures.json"
python manage.py dumpdata --exclude auth.permission --exclude contenttypes > $temp_file_name
echo "Review the migrated fixtures at ./$temp_file_name"
