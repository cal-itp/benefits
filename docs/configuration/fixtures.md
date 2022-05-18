# Fixtures

!!! example "Sample files"

    [`fixtures/*.json`][fixtures-sample]

!!! tldr "Django docs"

    [Providing data with fixtures][django-data-fixtures]

## Introduction

Fixtures are simply JSON representations of the app's model classes, defined in [`benefits/core/models.py`][core-models].

Fixture files are loaded as the application starts up and seed the configuration database. See the [`bin/init.sh`][init] script.

The fixture samples provided in the repository are sufficient to run the app locally and interact with e.g. the sample Transit
Agencies.

During the [deployment](../deployment/README.md) process, environment-specific fixtures are used to build that
environment's configuration database.

## Sample data

The sample data included in the repository fixtures is enough to bootstrap the application with basic functionality:

* Multiple transit agency configurations
* Multiple eligibility verification pathways
* With and without authentication required before eligibility verification
* In concert with the [sample eligibility server][eligibility-server], verification with test user data

### Not included

Some configuration data is not available with the samples in the repository:

* OAuth configuration to enable authentication (read more about [OAuth configuration](oauth.md))
* Rate Limiting configuration for eligibility
* reCAPTCHA configuration for user-submitted forms
* Payment processor configuration for the enrollment phase
* Amplitude configuration for capturing analytics events

### Sample transit agency: `ABC`

* Presents the user a choice between two different eligibility pathways
* One eligibility verifier requires authentication
* One eligibility verifier does not require authentication

### Sample transit agency: `DefTL`

* Single eligibility pathway, no choice presented to the user
* Eligibility verifier does not require authentication

## Building the configuration database

When local fixture files change, the configuration database needs to be rebuilt.

The file is called `django.db` and the following commands will rebuild it.

Run these commands from within the repository root, inside the devcontainer:

```bash
rm django.db

bin/init.sh
```

## Fixture source

The `bin/init.sh` script uses the [`DJANGO_INIT_PATH`][env-django-init] environment variable when loading fixture(s).

## Cypress test fixtures

Some of the tests also make use of the sample fixtures in the repository. See [`tests/cypress/fixtures/`][cypress-fixtures] for
more information.

[core-models]: https://github.com/cal-itp/benefits/blob/dev/benefits/core/models.py
[cypress-fixtures]: https://github.com/cal-itp/benefits/tree/dev/tests/cypress/fixtures
[django-data-fixtures]: https://docs.djangoproject.com/en/3.2/howto/initial-data/#providing-data-with-fixtures
[eligibility-server]: https://docs.calitp.org/eligibility-server
[env-django-init]: environment-variables.md#djangoinitpath
[fixtures-sample]: https://github.com/cal-itp/benefits/tree/dev/fixtures
[init]: https://github.com/cal-itp/benefits/blob/dev/bin/init.sh
