# Django models and migrations

!!! example "Models and migrations"

    [`benefits/core/models.py`][core-models]

    [`benefits/core/migrations/0001_initial.py`][core-migrations]

Cal-ITP Benefits defines a number of [models][core-models] in the core application, used throughout the codebase to configure
different parts of the UI and logic.

The Cal-ITP Benefits database is a simple Sqlite database that mostly acts as a read-only configuration store.
Runtime configuration changes can be persisted via [Django's Admin interface](https://docs.djangoproject.com/en/5.0/ref/contrib/admin/).

## Updating models

When models are updated, new migrations must be generated to reflect those changes into the configuration database.

A simple helper script exists to generate migrations based on the current state of models in the local directory:

[`bin/makemigrations.sh`][makemigrations]

```bash
bin/makemigrations.sh
```

This script:

1. Runs the django `makemigrations` command
1. Formats the newly regenerated migration file with `black`

Commit the new migration file along with the model changes.

## Updating fixtures

In addition to generating new migrations when models are updated, our fixture files which are used for development need to be updated.

As mentioned in [Loading sample data](../../tutorials/load-sample-data.md#not-included), we maintain private fixture files with working values for external integrations that are not included in the sample fixtures.

An easy way to update these fixture files is to run them through the migrations that were created. The steps in general are:

1. Download the fixtures that you need to update
1. Set `$DJANGO_DB_FIXTURES` to that file
1. Checkout the commit on `main` prior to the model changes (i.e. where the fixtures can be loaded in)
1. Run `./bin/reset_db.sh` to reset your database and load in the fixtures
1. Checkout the commit with the new model changes (most likely, the latest commit on `main`)
1. Run `./bin/init.sh` to apply migrations
1. Export the migrated fixtures to a temporary file
1. Review the migrated fixtures, and do any clean-up needed or manual updating needed (though generally we should be able to have data migrations that make it so no manual updating is needed)
1. Save the updated fixtures back

A helper script at [`bin/dumpdata.sh`][dumpdata] handles some of these steps, prompting where input is needed, so the steps are simplified down to:

1. Download the fixtures that you need to update
1. Set `$DJANGO_DB_FIXTURES` to that file
1. Run `./bin/dumpdata.sh`
1. Review the migrated fixtures, and do any clean-up needed or manual updating needed (though generally we should be able to have data migrations that make it so no manual updating is needed)
1. Save the updated fixtures back

[core-models]: https://github.com/cal-itp/benefits/blob/main/benefits/core/models.py
[core-migrations]: https://github.com/cal-itp/benefits/blob/main/benefits/core/migrations/0001_initial.py
[dumpdata]: https://github.com/cal-itp/benefits/blob/main/bin/dumpdata.sh
[makemigrations]: https://github.com/cal-itp/benefits/blob/main/bin/makemigrations.sh
