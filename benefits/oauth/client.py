import logging

from django.conf import settings

from authlib.integrations.django_client import OAuth


logger = logging.getLogger(__name__)


_OPENID_SCOPE = "openid"


def instance(scope=None):
    """
    Get an OAuth client instance using the OAUTH_CLIENT_NAME setting.

    Optionally configure with a (space-separated) scope.
    """
    if settings.OAUTH_CLIENT_NAME:
        logger.debug(f"Using OAuth client configuration: {settings.OAUTH_CLIENT_NAME}")

        oauth = OAuth()
        oauth.register(settings.OAUTH_CLIENT_NAME)
        client = oauth.create_client(settings.OAUTH_CLIENT_NAME)
    else:
        raise Exception("OAUTH_CLIENT_NAME is not configured")

    scopes = [_OPENID_SCOPE]

    if scope:
        scopes.append(scope)

    client.client_kwargs["scope"] = " ".join(scopes)

    return client
