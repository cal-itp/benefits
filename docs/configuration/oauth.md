# OAuth settings

Benefits can be configured to require users to authenticate with an OAuth [Open ID Connect (OIDC)](https://openid.net/connect/)
provider, before allowing the user to begin the Eligibility Verification process.

This section describes the related settings and how to configure the application to enable this feature.

## Authlib

!!! tldr "Authlib docs"

    Read more about [configuring Authlib for Django](https://docs.authlib.org/en/latest/client/django.html)

Benefits uses the open-source [Authlib](https://authlib.org/) for OAuth and OIDC client implementation. See the Authlib docs
for more details about what features are available. Specifically, from Authlib we:

1. Register an OAuth `client` using the configured [Django settings](#django-settings)
1. Call `client.authorize_redirect()` to send the user into the OIDC server's authentication flow, with our authorization
   callback URL
1. Upon the user returning from the OIDC Server with an access token, call `client.authorize_access_token()` to get a validated
   id token from the OIDC server

## Environment variables

!!! warning

    The following environment variables are all required for OAuth configuration

### `DJANGO_OAUTH_AUTHORITY`

Base address of the OAuth/OIDC server to use for authorization.

### `DJANGO_OAUTH_CLIENT_ID`

This application's client ID, as registered with the OAuth/OIDC server.

### `DJANGO_OAUTH_CLIENT_NAME`

The internal label of the OAuth client within this application.

See the [`OAUTH_CLIENT_NAME`](#oauth_client_name) setting for more.

### `DJANGO_OAUTH_SCOPE`

Space separated list of OAuth scope(s) to request from the OAuth/OIDC server.

Must include at least `openid`.

## Django settings

There are a few relevant settings defined in [`benefits/settings.py`][benefits-settings] related to OAuth.

### `OAUTH_CLIENT_NAME`

A `str` defining the application's internal label for the OAuth client that is used.

The app uses the value of this variable to further configure the OAuth feature, or skip that configuration for empty or `None`.

The value is initialized from the [`DJANGO_OAUTH_CLIENT_NAME`](#django_oauth_client_name) environment variable.

### `AUTHLIB_OAUTH_CLIENTS`

!!! tldr "Authlib docs"

    Read more about [configuring Authlib for Django](https://docs.authlib.org/en/latest/client/django.html#configuration)

A `dict` of OAuth client configurations this app may use.

By default, contains a single entry, keyed by [`OAUTH_CLIENT_NAME`](#oauth_client_name) and using the other
[`DJANGO_OAUTH_*` environment variables](#environment-variables) to populate the client's settings.

[benefits-settings]: https://github.com/cal-itp/benefits/blob/dev/benefits/settings.py
