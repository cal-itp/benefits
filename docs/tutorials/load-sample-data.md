# Loading sample data

!!! example "Sample data fixtures"

    [`benefits/core/migrations/local_fixtures.json`][sample-fixtures]

!!! tldr "Django docs"

    [How to provide initial data for models][django-load-initial-data]

## Introduction

The app's model classes are defined in [`benefits/core/models.py`][core-models].

Migrations are run as the application starts up. See the [`bin/init.sh`][init] script.

The sample values provided in the repository are sufficient to run the app locally and interact with e.g. the sample Transit
Agencies. [Django fixtures][django-fixtures] are used to load the database with sample data when running locally.

During the [deployment](../explanation/deployment.md) process, some environment-specific values are set in environment variables and read dynamically at runtime. Most configuration values are managed directly in the Django Admin interface at the `/admin` endpoint.

## Sample data

The sample data included in the repository is enough to bootstrap the application with basic functionality:

- Multiple transit agency configurations
- Multiple eligibility verification pathways
- With and without authentication required before eligibility verification
- In concert with the [sample eligibility server][eligibility-server], verification with test user data

### Not included

Some configuration data is not available with the samples in the repository:

- OAuth configuration to enable authentication
- reCAPTCHA configuration for user-submitted forms
- Transit processor configuration for the enrollment phase
- Amplitude configuration for capturing analytics events

Compiler developers, instead of setting these manually, you can load some of them with a private fixtures file that we maintain:

1. Grab the "Benefits fixtures with secrets for local development" note from our shared notes in LastPass
1. Put it in a new JSON file named something like `dev_fixtures.json`
1. Change the value of `DJANGO_DB_FIXTURES` in your `.env` file to point to your new `dev_fixtures.json`
1. Rebuild the devcontainer

## Rebuilding the configuration database locally

A local Django database will be initialized upon first startup of the devcontainer.

To rebuild the local Django database, run the [`bin/reset_db.sh`][reset-db] script from within the repository root,
inside the devcontainer:

```bash
bin/reset_db.sh
```

See the [Django Environment Variables](../reference/environment-variables.md#django) section for details about how to configure the local
database rebuild.

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

As mentioned above in the section about sample data that is [not included](#not-included), we maintain private fixture files with working values for external integrations that are not included in the sample fixtures.

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
[django-fixtures]: https://docs.djangoproject.com/en/5.2/topics/db/fixtures/
[django-load-initial-data]: https://docs.djangoproject.com/en/5.2/howto/initial-data/
[dumpdata]: https://github.com/cal-itp/benefits/blob/main/bin/dumpdata.sh
[eligibility-server]: https://docs.calitp.org/eligibility-server
[init]: https://github.com/cal-itp/benefits/blob/main/bin/init.sh
[makemigrations]: https://github.com/cal-itp/benefits/blob/main/bin/makemigrations.sh
[reset-db]: https://github.com/cal-itp/benefits/blob/main/bin/reset_db.sh
[sample-fixtures]: https://github.com/cal-itp/benefits/tree/main/benefits/core/migrations/local_fixtures.json
