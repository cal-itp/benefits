# Environment variables

!!! example "Sample file"

    [`.devcontainer/.env.sample`][env-sample]

The first steps of the Getting Started guide have you [create an `.env` file from the sample][getting-started_create-env].
The sections below outline the core environment variables and their purpose.

See other topic pages in this section for more specific environment variable configurations.

## Docker

### `COMPOSE_PROJECT_NAME`

!!! tldr "Docker docs"

    Read more at <https://docs.docker.com/compose/reference/envvars/#compose_project_name>

Name that Docker Compose prefixes to the project for container runs.

## Amplitude

!!! tldr "Amplitude API docs"

    Read more at <https://developers.amplitude.com/docs/http-api-v2#request-format>

### `ANALYTICS_KEY`

Amplitude API key for the project where the app will direct events.

If blank or an invalid key, analytics events aren't captured (though may still be logged).

## AWS

### `AWS_ACCESS_KEY_ID`

The AWS access key ID for a deployment environment.

Mostly not used in local settings. See the docs on [Deployment][deployment] for more.

### `AWS_BUCKET`

The AWS bucket for a deployment environment, where the environment file and fixtures for that environment are stored.

Mostly not used in local settings. See the docs on [Deployment][deployment] for more.

### `AWS_DEFAULT_REGION`

The AWS region for a deployment environment.

Mostly not used in local settings. See the docs on [Deployment][deployment] for more.

### `AWS_SECRET_ACCESS_KEY`

The AWS access key ID for a deployment environment.

Mostly not used in local settings. See the docs on [Deployment][deployment] for more.

### `CONFIG_FILE`

The (single) fixture file AWS uses for a deployment environment.

Mostly not used in local settings. See the docs on [Deployment][deployment] for more.

## Django

### `DJANGO_ADMIN`

Boolean:

* `True`: activates Django's built-in admin interface for content authoring.
* `False`: skips this activation.

### `DJANGO_ALLOWED_HOSTS`

!!! tldr "Django docs"

    [Settings: `ALLOWS_HOSTS`](https://docs.djangoproject.com/en/3.2/ref/settings/#allowed-hosts)

A list of strings representing the host/domain names that this Django site can serve.

### `DJANGO_DB`

String; names the database that Django uses for configuration.

### `DJANGO_DEBUG`

!!! tldr "Django docs"

    [Settings: `DEBUG`](https://docs.djangoproject.com/en/3.2/ref/settings/#debug)

Boolean; whether or not the application is launched in debug mode.

### `DJANGO_INIT_PATH`

The path to the fixture file(s) used to initialize the Django configuration database.

See [Fixtures](fixtures.md) for more.

### `DJANGO_LOCAL_PORT`

The port used to serve the Django application from the _host_ machine (that is running the application container).

i.e. if you are running the app in Docker on your local machine, this is the port that the app will be accessible from at
<http://localhost:$DJANGO_LOCAL_PORT>

From inside the container, the app is always listening on port `8000`.

### `DJANGO_LOG_LEVEL`

!!! tldr "Django docs"

    [Settings: `LOGGING_CONFIG`](https://docs.djangoproject.com/en/3.2/ref/settings/#logging-config)

The log level used in the application's logging configuration.

By default the application sends logs to `stdout`.

### `DJANGO_SECRET_KEY`

!!! tldr "Django docs"

    [Settings: `SECRET_KEY`](https://docs.djangoproject.com/en/3.2/ref/settings/#secret-key)

Django's primary secret, keep this safe!

### `DJANGO_TRUSTED_ORIGINS`

!!! tldr "Django docs"

    [Settings: `CSRF_TRUSTED_ORIGINS`](https://docs.djangoproject.com/en/3.2/ref/settings/#csrf-trusted-origins)

Comma-separated list of hosts which are trusted origins for unsafe requests (e.g. POST)

## Cypress tests

!!! tldr "Cypress docs"

    [`CYPRESS_*` variables](https://docs.cypress.io/guides/guides/environment-variables#Option-3-CYPRESS_)

### `CYPRESS_baseUrl`

The base URL for the (running) application, against which all Cypress `.visit()` etc. commands are run.

When Cypress is running inside the devcontainer, this should be `http://localhost:8000`. When Cypress is running outside the
devcontainer, check the [`DJANGO_LOCAL_PORT`](#djangolocalport).

[deployment]: ../deployment/README.md
[env-sample]: https://github.com/cal-itp/benefits/blob/dev/.devcontainer/.env.sample
[getting-started_create-env]: ../getting-started/README.md#create-an-environment-file
