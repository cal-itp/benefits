# Django models and migrations

!!! example "Models and migrations"

    [`benefits/core/models.py`][core-models]

    [`benefits/core/migrations/0001_initial.py`][core-migrations]

Cal-ITP Benefits defines a number of [models][core-models] in the core application, used throughout the codebase to configure
different parts of the UI and logic.

The Cal-ITP Benefits database is a simple read-only Sqlite database, initialized from the [data migration](../configuration/data.md) files.

## Migrations

The database is rebuilt from scratch each time the container starts. We maintain a few [migration][core-migrations] files that set up the schema and load initial data.

These files always represent the current schema and data for the database and match the current structure of the model classes.

## Updating models

When models are updated, the migration should be updated as well.

A simple helper script exists to regenerate the migration file based on the current state of models in the local directory:

[`bin/makemigrations.sh`][makemigrations]

```bash
bin/makemigrations.sh
```

This script:

1. Copies the existing migration files to a temporary directory
1. Runs the django `makemigrations` command
1. Copies back any migration files that are missing (data migration files)
1. Formats the newly regenerated schema migration file with `black`

This will result in a simple diff of changes on the schema migration file. Commit these changes (including the timestamp!) along with the model changes.

[core-models]: https://github.com/cal-itp/benefits/blob/dev/benefits/core/models.py
[core-migrations]: https://github.com/cal-itp/benefits/blob/dev/benefits/core/migrations
[makemigrations]: https://github.com/cal-itp/benefits/blob/dev/bin/makemigrations.sh
