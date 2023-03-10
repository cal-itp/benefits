# Configuration data

!!! example "Sample data provided by data migration"

    [`benefits/core/migrations/0002_sample_data.py`][data-sample]

!!! example "Helper migration file to define data migration order"

    [`benefits/core/migrations/0003_data_migration_order.py`][helper-migration]

    Since our initial data migration files are assumed to start with `0002` and depend only on `0001_initial`, this migration file ensures the migration graph has a defined order (which is required for the migration to run). It looks in the `benefits/core/migrations` directory for migration files starting with `0002` and declares them in its dependencies list.

!!! tldr "Django docs"

    [How to provide initial data for models][django-load-initial-data]

## Introduction

Django [data migrations](https://docs.djangoproject.com/en/4.0/topics/migrations/#data-migrations) are used to load the database with instances of the app's model classes, defined in [`benefits/core/models.py`][core-models].

Migrations are run as the application starts up. See the [`bin/init.sh`][init] script.

The sample data provided in the repository is sufficient to run the app locally and interact with e.g. the sample Transit
Agencies.

During the [deployment](../deployment/README.md) process, an environment-specific data migration is used to build that
environment's configuration database.

## Sample data

The sample data included in the repository is enough to bootstrap the application with basic functionality:

- Multiple transit agency configurations
- Multiple eligibility verification pathways
- With and without authentication required before eligibility verification
- In concert with the [sample eligibility server][eligibility-server], verification with test user data

### Not included

Some configuration data is not available with the samples in the repository:

- OAuth configuration to enable authentication (read more about [OAuth configuration](oauth.md))
- Rate Limiting configuration for eligibility
- reCAPTCHA configuration for user-submitted forms
- Payment processor configuration for the enrollment phase
- Amplitude configuration for capturing analytics events

### Sample transit agency: `ABC`

- Presents the user a choice between two different eligibility pathways
- One eligibility verifier requires authentication
- One eligibility verifier does not require authentication

### Sample transit agency: `DefTL`

- Single eligibility pathway, no choice presented to the user
- Eligibility verifier does not require authentication

## Building the configuration database

When the data migration changes, the configuration database needs to be rebuilt.

The file is called `django.db` and the following commands will rebuild it.

Run these commands from within the repository root, inside the devcontainer:

```bash
bin/init.sh
```

[core-models]: https://github.com/cal-itp/benefits/blob/dev/benefits/core/models.py
[django-load-initial-data]: https://docs.djangoproject.com/en/4.0/howto/initial-data/
[eligibility-server]: https://docs.calitp.org/eligibility-server
[data-sample]: https://github.com/cal-itp/benefits/tree/dev/benefits/core/migrations/0002_sample_data.py
[helper-migration]: https://github.com/cal-itp/benefits/tree/dev/benefits/core/migrations/0003_data_migration_order.py
[init]: https://github.com/cal-itp/benefits/blob/dev/bin/init.sh
