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

[core-models]: https://github.com/cal-itp/benefits/blob/dev/benefits/core/models.py
[core-migrations]: https://github.com/cal-itp/benefits/blob/dev/benefits/core/migrations/0001_initial.py
[makemigrations]: https://github.com/cal-itp/benefits/blob/dev/bin/makemigrations.sh
