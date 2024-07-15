# Admin interface

!!! tldr "Django docs"

    [The Django admin site](https://docs.djangoproject.com/en/5.0/ref/contrib/admin/)

The configuration values that can be stored in the application database are managed directly in the [Django Admin interface](./admin-interface.md) at the `/admin` endpoint.

Single sign-on authentication is supported by the admin interface using [`django-google-sso`](https://megalus.github.io/django-google-sso/).


## Environment variables

!!! tldr "`django-google-sso` docs"

    [All settings for `django-google-sso`](https://megalus.github.io/django-google-sso/settings/)

!!! info "`settings.py`"

    Configuration of `django-google-sso` in [Benefits settings](https://github.com/cal-itp/benefits/blob/4625f250f48eb9071d9b8fdc79e4dfc6cb2ee625/benefits/settings.py#L61-L74)

These environment variables must be set in your `.env` file to use the admin interface locally:

### GOOGLE_SSO_CLIENT_ID

> The Google OAuth 2.0 Web Application Client ID.

### GOOGLE_SSO_PROJECT_ID

> The Google OAuth 2.0 Project ID.

### GOOGLE_SSO_CLIENT_SECRET

> The Google OAuth 2.0 Web Application Client Secret.

### GOOGLE_SSO_ALLOWABLE_DOMAINS

> List of domains that will be allowed to create users.

### GOOGLE_SSO_STAFF_LIST

> List of emails that will be created as staff.

### GOOGLE_SSO_SUPERUSER_LIST

> List of emails that will be created as superuser.
