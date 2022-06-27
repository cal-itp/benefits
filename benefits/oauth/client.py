"""
The oauth application: helpers for working with OAuth clients.
"""

import logging

from authlib.integrations.django_client import OAuth

from benefits.core.models import AuthProvider


logger = logging.getLogger(__name__)

oauth = OAuth()


def _client_kwargs(scope=None):
    """
    Generate the OpenID Connect client_kwargs, with optional extra scope(s).

    `scope` should be a space-separated list of scopes to add.
    """
    scopes = ["openid", scope] if scope else ["openid"]
    return {"code_challenge_method": "S256", "scope": " ".join(scopes)}


def _server_metadata_url(authority):
    """
    Generate the OpenID Connect server_metadata_url for an OAuth authority server.

    `authority` should be a fully qualified HTTPS domain name, e.g. https://example.com.
    """
    return f"{authority}/.well-known/openid-configuration"


def register_providers(oauth_registry):
    """
    Register OAuth clients into the given registry, using configuration from AuthProvider models.

    Adapted from https://stackoverflow.com/a/64174413.
    """
    logger.info("Registering OAuth clients")

    providers = AuthProvider.objects.all()

    for provider in providers:
        logger.debug(f"Registering OAuth client: {provider.client_name}")

        oauth_registry.register(
            provider.client_name,
            client_id=provider.client_id,
            server_metadata_url=_server_metadata_url(provider.authority),
            client_kwargs=_client_kwargs(provider.scope),
        )
