# OAuth settings

Benefits can be configured to require users to authenticate with an OAuth [Open ID Connect (OIDC)](https://openid.net/connect/)
provider, before allowing the user to begin the Eligibility Verification process.

This section describes the related settings and how to configure the application to enable this feature.

## Authlib

!!! tldr "Authlib docs"

    Read more about [configuring Authlib for Django](https://docs.authlib.org/en/latest/client/django.html)

Benefits uses the open-source [Authlib](https://authlib.org/) for OAuth and OIDC client implementation. See the Authlib docs
for more details about what features are available. Specifically, from Authlib we:

1. Create an OAuth client using the [Django configuration](#django-configuration)
1. Call `client.authorize_redirect()` to send the user into the OIDC server's authentication flow, with our authorization
   callback URL
1. Upon the user returning from the OIDC Server with an access token, call `client.authorize_access_token()` to get a validated
   id token from the OIDC server

## Django configuration

OAuth settings are configured as instances of the [`IdentityGatewayConfig` model][cdt-identity-model] (defined in the [`cdt_identity`][cdt-identity] Django application) and [`EnrollmentFlow` model](../development/models-migrations.md).

The [data migration file](./data.md) contains sample values for a `IdentityGatewayConfig` and `EnrollmentFlow` configuration. You can set values for a real Open ID Connect provider in environment variables so that they are used instead of the sample values.

## Django usage

The [`benefits.oauth.client`][oauth-client] module defines helpers for registering OAuth clients, and creating instances for
use in e.g. views.

- `oauth` is an `authlib.integrations.django_client.OAuth` instance

Consumers call `benefits.oauth.client.create_client(oauth, flow)` with an `EnrollmentFlow` to obtain an Authlib client
instance. If a client for the flow has not been registered yet, `_register_provider(oauth_registry, flow)` uses data from the
given `EnrollmentFlow` to register the client into this instance and returns the client object.

[oauth-client]: https://github.com/cal-itp/benefits/blob/main/benefits/oauth/client.py
[cdt-identity]: https://github.com/Office-of-Digital-Services/django-cdt-identity
[cdt-identity-model]: https://github.com/Office-of-Digital-Services/django-cdt-identity/blob/main/cdt_identity/models.py
