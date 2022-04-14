import logging

from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import urlencode

from authlib.integrations.django_client import OAuth

from benefits.core import session
from benefits.settings import OAUTH_CLIENT_NAME


logger = logging.getLogger(__name__)


if OAUTH_CLIENT_NAME:
    logger.debug(f"Using OAuth client configuration: {OAUTH_CLIENT_NAME}")

    _oauth = OAuth()
    _oauth.register(OAUTH_CLIENT_NAME)
    oauth_client = _oauth.create_client(OAUTH_CLIENT_NAME)


ROUTE_AUTH = "oauth:authorize"
ROUTE_START = "eligibility:start"
ROUTE_CONFIRM = "eligibility:confirm"


def login(request):
    if not oauth_client:
        raise Exception("No OAuth client")

    route = reverse(ROUTE_AUTH)
    redirect_uri = request.build_absolute_uri(route)

    logger.debug(f"OAuth authorize_redirect with redirect_uri: {redirect_uri}")

    return oauth_client.authorize_redirect(request, redirect_uri)


def authorize(request):
    if not oauth_client:
        raise Exception("No OAuth client")

    logger.debug("Attempting to authorize OAuth access token")
    token = oauth_client.authorize_access_token(request)

    if token is None:
        logger.warning("Could not authorize OAuth access token")
        return redirect(ROUTE_START)
    else:
        # we are intentionally not storing anything about the user, including their token
        logger.debug("OAuth access token authorized")
        session.update(request, auth=True)
        return redirect(ROUTE_CONFIRM)


def logout(request):
    """View implementing application signout, e.g. updating the Django session."""

    session.update(request, auth=False)
    return redirect(ROUTE_START)


def _deauthorize_redirect(token, redirect_url):
    """Helper implements OIDC signout via the `end_session_endpoint`."""

    # Authlib has not yet implemented `end_session_endpoint` as the OIDC Session Management 1.0 spec is still in draft
    # See https://github.com/lepture/authlib/issues/331#issuecomment-827295954 for more
    #
    # The implementation here was adapted from the same ticket: https://github.com/lepture/authlib/issues/331#issue-838728145

    if not oauth_client:
        raise Exception("No OAuth client")

    metadata = oauth_client.load_server_metadata()
    end_session_endpoint = metadata.get("end_session_endpoint")

    params = dict(id_token_hint=token["id_token"], post_logout_redirect_uri=redirect_url)
    encoded_params = urlencode(params)
    end_session_url = f"{end_session_endpoint}?{encoded_params}"

    return redirect(end_session_url)
