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

"Staff" refers to Django's concept of a user with `is_staff` set to `True`, which means they can log in, and also to the Cal-ITP Benefits concept of a user who should have a "Cal-ITP staff" level of access to configuration values.

### GOOGLE_SSO_SUPERUSER_LIST

> List of emails that will be created as superuser.

## To add a new user:
- Add the user's email to either `GOOGLE_SSO_STAFF_LIST` or `GOOGLE_SSO_SUPERUSER_LIST` depending on what permissions they should have.
   - The email must be from a domain that is in the `GOOGLE_SSO_ALLOWABLE_DOMAINS` list.
- Restart the Benefits application so that Django settings are re-loaded.
- Have the user log in to the admin interface with their Google account.
