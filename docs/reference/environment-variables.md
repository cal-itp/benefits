# Environment variables

The first steps of the Getting Started guide mention [creating an `.env` file][getting-started_create-env].

The sections below outline in more detail the application environment variables that you may want to override, and their purpose.
In Azure App Services, this is more generally called the ["configuration"][app-service-config].

See other topic pages in this section for more specific environment variable configurations.

!!! warning "Multiline environment variables"

    Although Docker, bash, etc. support multiline values directly in e.g. an .env file:

    ```bash
    multi_line_value='first line
    second line
    third line'
    ```

    The VS Code Python extension does not parse multiline values: https://code.visualstudio.com/docs/python/environments#_environment-variables

    When specifying multiline values for local usage, use the literal newline character `\n` but maintain the single quote wrapper:

    ```bash
    multi_line_value='first line\nsecond line\third line'
    ```

    A quick bash script to convert direct multiline values to their literal newline character equivalent is:

    ```bash
    echo "${multi_line_value//$'\n'/\\n}"
    ```

## Amplitude

!!! tldr "Amplitude API docs"

    Read more at <https://developers.amplitude.com/docs/http-api-v2#request-format>

### `ANALYTICS_KEY`

!!! warning "Deployment configuration"

    You may change this setting when deploying the app to a non-localhost domain

Amplitude API key for the project where the app will direct events.

If blank or an invalid key, analytics events aren't captured (though may still be logged).

## Django

### `DJANGO_ALLOWED_HOSTS`

!!! warning "Deployment configuration"

    You must change this setting when deploying the app to a non-localhost domain

!!! tldr "Django docs"

    [Settings: `ALLOWS_HOSTS`](https://docs.djangoproject.com/en/5.0/ref/settings/#allowed-hosts)

A list of strings representing the host/domain names that this Django site can serve.

### `DJANGO_STORAGE_DIR`

!!! warning "Deployment configuration"

    You may change this setting when deploying the app to a non-localhost domain

The directory where Django creates its SQLite database file and where it creates the `uploads` folder for file uploads.
_Must exist and be writable by the Django process._

By default, the base project directory (i.e. the root of the repository).

### `DJANGO_DB_FILE`

!!! info "Local configuration"

    This setting only affects the app running on localhost

The name of the Django database file to use locally (during both normal app startup and for resetting the database).

By default, `django.db`.

### `DJANGO_DB_FIXTURES`

!!! info "Local configuration"

    This setting only affects the app running on localhost

A path, relative to the repository root, of Django data fixtures to load when resetting the database.

The file must end in `fixtures.json` for the script to process it correctly.

By default, `benefits/core/migrations/local_fixtures.json`.

### `DJANGO_DB_RESET`

!!! info "Local configuration"

    This setting only affects the app running on localhost

Boolean:

- `True` (default): deletes the existing database file and runs fresh Django migrations.
- `False`: Django uses the existing database file.
  (Note: Fixtures will still be loaded, updating any values on those objects if they have changed.)

### `DJANGO_DEBUG`

!!! warning "Deployment configuration"

    Do not enable this in production

!!! tldr "Django docs"

    [Settings: `DEBUG`](https://docs.djangoproject.com/en/5.0/ref/settings/#debug)

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

    [Settings: `LOGGING`](https://docs.djangoproject.com/en/5.0/ref/settings/#logging)

The log level used in the application's logging configuration.
Defaults to `DEBUG` when Django is running in debug mode and `WARNING` otherwise.

By default the application sends logs to `stdout`.

### `DJANGO_SECRET_KEY`

!!! warning "Deployment configuration"

    You must change this setting when deploying the app to a non-localhost domain

!!! tldr "Django docs"

    [Settings: `SECRET_KEY`](https://docs.djangoproject.com/en/5.0/ref/settings/#secret-key)

Django's primary secret, keep this safe!

### `DJANGO_SUPERUSER_EMAIL`

!!! info "Local configuration"

    This setting only affects the app running on localhost

The email address of the Django Admin superuser created when resetting the database.

### `DJANGO_SUPERUSER_PASSWORD`

!!! info "Local configuration"

    This setting only affects the app running on localhost

The password of the Django Admin superuser created when resetting the database.

### `DJANGO_SUPERUSER_USERNAME`

!!! info "Local configuration"

    This setting only affects the app running on localhost

The username of the Django Admin superuser created when resetting the database.

### `DJANGO_TRUSTED_ORIGINS`

!!! warning "Deployment configuration"

    You must change this setting when deploying the app to a non-localhost domain

!!! tldr "Django docs"

    [Settings: `CSRF_TRUSTED_ORIGINS`](https://docs.djangoproject.com/en/5.0/ref/settings/#csrf-trusted-origins)

Comma-separated list of hosts which are trusted origins for unsafe requests (e.g. POST)

### `HEALTHCHECK_USER_AGENTS`

!!! warning "Deployment configuration"

    You must change this setting when deploying the app to a non-localhost domain

Comma-separated list of User-Agent strings which, when present as an HTTP header, should only receive healthcheck responses. Used by our `HealthcheckUserAgents` middleware.

## Django admin interface

!!! tldr "Django docs"

    [The Django admin site](https://docs.djangoproject.com/en/5.0/ref/contrib/admin/)

The configuration values that can be stored in the application database are managed directly in the [Django Admin interface](./admin-interface.md) at the `/admin` endpoint.

Single sign-on authentication is supported by the admin interface using [`django-google-sso`](https://megalus.github.io/django-google-sso/).

These environment variables can be set in your `.env` file to use certain features in the admin interface locally:

### AZURE_COMMUNICATION_CONNECTION_STRING

!!! info "`settings.py`"

    Usage of `AZURE_COMMUNICATION_CONNECTION_STRING` in [Benefits settings](https://github.com/cal-itp/benefits/blob/main/benefits/settings.py#L396)

The connection string needed to use an Azure Communication Service for sending emails, such as the one for user password reset. If this variable is not set, the file-based email backend is used.

In deployed instances, this is automatically set by Terraform by referencing the [`azurerm_communication_service.primary_connection_string`](https://github.com/cal-itp/benefits/blob/main/terraform/email.tf#L15) attribute.

### DEFAULT_FROM_EMAIL

!!! tldr "Django docs"

    [Settings: `DEFAULT_FROM_EMAIL`](https://docs.djangoproject.com/en/5.2/ref/settings/#default-from-email)

The email address used by default in the `From:` header of outgoing emails.

### GOOGLE_SSO_CLIENT_ID

!!! tldr "`django-google-sso` docs"

    [All settings for `django-google-sso`](https://megalus.github.io/django-google-sso/settings/)

!!! info "`settings.py`"

    Configuration of `django-google-sso` in [Benefits settings](https://github.com/cal-itp/benefits/blob/main/benefits/settings.py#L74-L90)

> The Google OAuth 2.0 Web Application Client ID.

### GOOGLE_SSO_PROJECT_ID

> The Google OAuth 2.0 Project ID.

### GOOGLE_SSO_CLIENT_SECRET

> The Google OAuth 2.0 Web Application Client Secret.

### GOOGLE_SSO_ALLOWABLE_DOMAINS

> List of domains that will be allowed to create users.

### GOOGLE_SSO_STAFF_LIST

> List of emails that will be created as staff.

"Staff" refers to Django's concept of a user with `is_staff` set to `True`, which means they can log in, and also to the Cal-ITP Benefits concept of a user who should have a "Cal-ITP staff" level of access to configuration values.

### GOOGLE_SSO_SUPERUSER_LIST

> List of emails that will be created as superuser.

## `requests` configuration

!!! tldr "`requests` docs"

    [Docs for timeouts](https://requests.readthedocs.io/en/latest/user/advanced/#timeouts)

### `REQUESTS_CONNECT_TIMEOUT`

The number of seconds `requests` will wait for the client to establish a connection to a remote machine. Defaults to 3 seconds.

### `REQUESTS_READ_TIMEOUT`

The number of seconds the client will wait for the server to send a response. Defaults to 1 second.

## Sentry

### `SENTRY_DSN`

!!! tldr "Sentry docs"

    [Data Source Name (DSN)](https://docs.sentry.io/product/sentry-basics/dsn-explainer/)

Enables [sending events to Sentry](../guides/troubleshooting.md#sentry).

### `SENTRY_ENVIRONMENT`

!!! tldr "Sentry docs"

    [`environment` config value](https://docs.sentry.io/platforms/python/configuration/options/#environment)

Segments errors by which deployment they occur in. This defaults to `dev`, and can be set to match one of the [environment names](../explanation/infrastructure.md#environments).

`local` may also be used for local testing of the Sentry integration.

### `SENTRY_REPORT_URI`

!!! tldr "Sentry docs"

    [Security Policy Reporting](https://docs.sentry.io/product/security-policy-reporting/)

Collect information on Content-Security-Policy (CSP) violations. Read more about [CSP configuration in Benefits](./content-security-policy.md).

To enable report collection, set this env var to the authenticated Sentry endpoint.

### `SENTRY_TRACES_SAMPLE_RATE`

!!! tldr "Sentry docs"

    [`traces_sample_rate`](https://docs.sentry.io/platforms/python/configuration/sampling/#configuring-the-transaction-sample-rate)

Control the volume of transactions sent to Sentry. Value must be a float in the range `[0.0, 1.0]`.

The default is `0.0` (i.e. no transactions are tracked).

[app-service-config]: https://docs.microsoft.com/en-us/azure/app-service/configure-common?tabs=portal
[getting-started_create-env]: ../guides/getting-started.md#create-an-environment-file
