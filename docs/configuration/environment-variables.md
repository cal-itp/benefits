# Environment variables

The first steps of the Getting Started guide mention [creating an `.env` file][getting-started_create-env].

The sections below outline in more detail the application environment variables that you may want to override, and their purpose. In App Service, this is more generally called the ["configuration"][app-service-config].

See other topic pages in this section for more specific environment variable configurations. See [benefits-secrets][benefits-secrets] for values.

## Docker

### `COMPOSE_PROJECT_NAME`

!!! info "Local configuration"

    This setting only affects the app running on localhost

!!! tldr "Docker docs"

    Read more at <https://docs.docker.com/compose/reference/envvars/#compose_project_name>

Name that Docker Compose prefixes to the project for container runs.

## Amplitude

!!! tldr "Amplitude API docs"

    Read more at <https://developers.amplitude.com/docs/http-api-v2#request-format>

### `ANALYTICS_KEY`

!!! warning "Deployment configuration"

    You may change this setting when deploying the app to a non-localhost domain

Amplitude API key for the project where the app will direct events.

If blank or an invalid key, analytics events aren't captured (though may still be logged).

## Django

### `DJANGO_ADMIN`

Boolean:

- `True`: activates Django's built-in admin interface for content authoring.
- `False` (default): skips this activation.

### `DJANGO_ALLOWED_HOSTS`

!!! warning "Deployment configuration"

    You must change this setting when deploying the app to a non-localhost domain

!!! tldr "Django docs"

    [Settings: `ALLOWS_HOSTS`](https://docs.djangoproject.com/en/4.0/ref/settings/#allowed-hosts)

A list of strings representing the host/domain names that this Django site can serve.

### `DJANGO_DEBUG`

!!! warning "Deployment configuration"

    Do not enable this in production

!!! tldr "Django docs"

    [Settings: `DEBUG`](https://docs.djangoproject.com/en/4.0/ref/settings/#debug)

Boolean:

- `True`: the application is launched with debug mode turned on, allows pausing on breakpoints in the code, changes how static
  files are served
- `False` (default): the application is launched with debug mode turned off, similar to how it runs in production

### `DJANGO_LOCAL_PORT`

!!! info "Local configuration"

    This setting only affects the app running on localhost

The port used to serve the Django application from the _host_ machine (that is running the application container).

i.e. if you are running the app in Docker on your local machine, this is the port that the app will be accessible from at
<http://localhost:$DJANGO_LOCAL_PORT>

From inside the container, the app is always listening on port `8000`.

### `DJANGO_LOG_LEVEL`

!!! warning "Deployment configuration"

    You may change this setting when deploying the app to a non-localhost domain

!!! tldr "Django docs"

    [Settings: `LOGGING_CONFIG`](https://docs.djangoproject.com/en/4.0/ref/settings/#logging-config)

The log level used in the application's logging configuration.

By default the application sends logs to `stdout`.

### `DJANGO_SECRET_KEY`

!!! warning "Deployment configuration"

    You must change this setting when deploying the app to a non-localhost domain

!!! tldr "Django docs"

    [Settings: `SECRET_KEY`](https://docs.djangoproject.com/en/4.0/ref/settings/#secret-key)

Django's primary secret, keep this safe!

### `DJANGO_TRUSTED_ORIGINS`

!!! warning "Deployment configuration"

    You must change this setting when deploying the app to a non-localhost domain

!!! tldr "Django docs"

    [Settings: `CSRF_TRUSTED_ORIGINS`](https://docs.djangoproject.com/en/4.0/ref/settings/#csrf-trusted-origins)

Comma-separated list of hosts which are trusted origins for unsafe requests (e.g. POST)

### `HEALTHCHECK_USER_AGENTS`

!!! warning "Deployment configuration"

    You must change this setting when deploying the app to a non-localhost domain

Comma-separated list of User-Agent strings which, when present as an HTTP header, should only receive healthcheck responses. Used by our `HealthcheckUserAgents` middleware.

## Cypress tests

!!! tldr "Cypress docs"

    [`CYPRESS_*` variables](https://docs.cypress.io/guides/guides/environment-variables#Option-3-CYPRESS_)

### `CYPRESS_baseUrl`

The base URL for the (running) application, against which all Cypress `.visit()` etc. commands are run.

When Cypress is running inside the devcontainer, this should be `http://localhost:8000`. When Cypress is running outside the
devcontainer, check the [`DJANGO_LOCAL_PORT`](#django_local_port).

## Sentry

### `SENTRY_DSN`

!!! tldr "Sentry docs"

    [Data Source Name (DSN)](https://docs.sentry.io/product/sentry-basics/dsn-explainer/)

Enables [sending events to Sentry](../../deployment/troubleshooting/#error-monitoring).

### `SENTRY_ENVIRONMENT`

!!! tldr "Sentry docs"

    [`environment` config value](https://docs.sentry.io/platforms/python/configuration/options/#environment)

Segments errors by which deployment they occur in. This defaults to `local`, and can be set to match one of the [environment names](../../deployment/infrastructure/#environments).

[app-service-config]: https://docs.microsoft.com/en-us/azure/app-service/configure-common?tabs=portal
[benefits-secrets]: https://github.com/cal-itp/benefits-secrets
[getting-started_create-env]: ../getting-started/README.md#create-an-environment-file
