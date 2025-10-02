# Configuration data

!!! example "Sample data fixtures"

    [`benefits/core/migrations/local_fixtures.json`][sample-fixtures]

!!! tldr "Django docs"

    [How to provide initial data for models][django-load-initial-data]

## Introduction

The app's model classes are defined in [`benefits/core/models.py`][core-models].

Migrations are run as the application starts up. See the [`bin/init.sh`][init] script.

The sample values provided in the repository are sufficient to run the app locally and interact with e.g. the sample Transit
Agencies. [Django fixtures][django-fixtures] are used to load the database with sample data when running locally.

During the [deployment](../deployment/README.md) process, some environment-specific values are set in environment variables and
read dynamically at runtime. Most configuration values are managed directly in the [Django Admin interface](./admin-interface.md) at the `/admin` endpoint.

## Sample data

The sample data included in the repository is enough to bootstrap the application with basic functionality:

- Multiple transit agency configurations
- Multiple eligibility verification pathways
- With and without authentication required before eligibility verification
- In concert with the [sample eligibility server][eligibility-server], verification with test user data

### Not included

Some configuration data is not available with the samples in the repository:

- OAuth configuration to enable authentication (read more about [OAuth configuration](oauth.md))
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

See the [Django Environment Variables](environment-variables.md#django) section for details about how to configure the local
database rebuild.

[core-models]: https://github.com/cal-itp/benefits/blob/main/benefits/core/models.py
[django-fixtures]: https://docs.djangoproject.com/en/5.0/topics/db/fixtures/
[django-load-initial-data]: https://docs.djangoproject.com/en/5.0/howto/initial-data/
[eligibility-server]: https://docs.calitp.org/eligibility-server
[init]: https://github.com/cal-itp/benefits/blob/main/bin/init.sh
[reset-db]: https://github.com/cal-itp/benefits/blob/main/bin/reset_db.sh
[sample-fixtures]: https://github.com/cal-itp/benefits/tree/main/benefits/core/migrations/local_fixtures.json
