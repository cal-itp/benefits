import logging

from django.conf import settings

from authlib.integrations.django_client import OAuth


_OAUTH_CLIENT = None


logger = logging.getLogger(__name__)


def instance():
    """
    Get the OAuth client instance using the OAUTH_CLIENT_NAME setting.
    """
    global _OAUTH_CLIENT
    if not _OAUTH_CLIENT:
        if settings.OAUTH_CLIENT_NAME:
            logger.debug(f"Using OAuth client configuration: {settings.OAUTH_CLIENT_NAME}")

            _oauth = OAuth()
            _oauth.register(settings.OAUTH_CLIENT_NAME)
            _OAUTH_CLIENT = _oauth.create_client(settings.OAUTH_CLIENT_NAME)
        else:
            raise Exception("OAUTH_CLIENT_NAME is not configured")

    return _OAUTH_CLIENT
