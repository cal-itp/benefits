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

## Building the configuration database

If you update your local fixtures, you'll need to rebuild the configuration database.

By default this file is called `django.db` (see the [`$DJANGO_DB`][env-django-db] environment variable) and the following
commands will rebuild it.

Run these from within the repository root, inside the devcontainer:

```bash
rm django.db

bin/init.sh
```

## Fixture source

The `bin/init.sh` script looks at the [`$DJANGO_INIT_PATH`][env-django-init] environment variable to determine which fixture(s)
to load.

## Cypress test fixtures

Some of the tests also make use of the sample fixtures in the repository. See [`tests/cypress/fixtures/`][cypress-fixtures] for
more information.

[core-models]: https://github.com/cal-itp/benefits/blob/dev/benefits/core/models.py
[cypress-fixtures]: https://github.com/cal-itp/benefits/tree/dev/tests/cypress/fixtures
[django-data-fixtures]: https://docs.djangoproject.com/en/3.2/howto/initial-data/#providing-data-with-fixtures
[env-django-db]: environment-variables.md#djangodb
[env-django-init]: environment-variables.md#djangoinitpath
[fixtures-sample]: https://github.com/cal-itp/benefits/tree/dev/fixtures
[init]: https://github.com/cal-itp/benefits/blob/dev/bin/init.sh
