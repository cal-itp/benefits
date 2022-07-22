# Django models and migrations

!!! example "Models and migrations"

    [`benefits/core/models.py`][core-models]

    [`benefits/core/migrations/0001_initial.py`][core-migrations]

Cal-ITP Benefits defines a number of [models][core-models] in the core application, used throughout the codebase to configure
different parts of the UI and logic.

The Cal-ITP Benefits database is a simple read-only Sqlite database, initialized from the [data migration](../configuration/data.md) files.

## Migrations

The database is rebuilt from scratch each time the container starts, so we maintain a single [migration][core-migrations] file.

This file always represents the current schema of the database and matches the current structure of the model classes.

## Updating models

When models are updated, the migration should be updated as well.

A simple helper script exists to regenerate the migration file based on the current state of models in the local directory:

[`bin/makemigrations.sh`][makemigrations]

```bash
bin/makemigrations.sh
```

This script:

1. Deletes the existing migrations file
1. Runs the django `makemigrations` command
1. Formats the newly regenerated file with `black`

This will result in a simple diff of changes on the same migration file. Commit these changes (including the timestamp!) along
with the model changes.

[core-models]: https://github.com/cal-itp/benefits/blob/dev/benefits/core/models.py
[core-migrations]: https://github.com/cal-itp/benefits/blob/dev/benefits/core/migrations/0001_initial.py
[makemigrations]: https://github.com/cal-itp/benefits/blob/dev/bin/makemigrations.sh
