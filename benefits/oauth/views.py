import logging

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import urlencode

from authlib.integrations.django_client import OAuth

from benefits.core import session
from . import analytics


logger = logging.getLogger(__name__)

if settings.OAUTH_CLIENT_NAME:
    logger.debug(f"Using OAuth client configuration: {settings.OAUTH_CLIENT_NAME}")

    _oauth = OAuth()
    _oauth.register(settings.OAUTH_CLIENT_NAME)
    oauth_client = _oauth.create_client(settings.OAUTH_CLIENT_NAME)


ROUTE_AUTH = "oauth:authorize"
ROUTE_START = "eligibility:start"
ROUTE_CONFIRM = "eligibility:confirm"
ROUTE_POST_LOGOUT = "oauth:post_logout"


def login(request):
    analytics.started_sign_in(request)

    if not oauth_client:
        raise Exception("No OAuth client")

    route = reverse(ROUTE_AUTH)
    redirect_uri = _generate_redirect_uri(request, route)

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

    logger.debug("OAuth access token authorized")

    # we store the id_token in the user's session
    # this is the minimal amount of information needed later to log the user out
    session.update(request, oauth_token=token["id_token"])

    analytics.finished_sign_in(request)

    return redirect(ROUTE_CONFIRM)


def logout(request):
    """View implementing OIDC and application sign out."""

    # overwrite the oauth session token, the user is signed out of the app
    token = session.oauth_token(request)
    session.logout(request)

    route = reverse(ROUTE_POST_LOGOUT)
    redirect_uri = _generate_redirect_uri(request, route)

    logger.debug(f"OAuth end_session_endpoint with redirect_uri: {redirect_uri}")

    # send the user through the end_session_endpoint, redirecting back to
    # the post_logout route
    return _deauthorize_redirect(token, redirect_uri)


def post_logout(request):
    """View routes the user to their origin after sign out."""

    origin = session.origin(request)
    return redirect(origin)


def _deauthorize_redirect(token, redirect_uri):
    """Helper implements OIDC signout via the `end_session_endpoint`."""

    # Authlib has not yet implemented `end_session_endpoint` as the OIDC Session Management 1.0 spec is still in draft
    # See https://github.com/lepture/authlib/issues/331#issuecomment-827295954 for more
    #
    # The implementation here was adapted from the same ticket: https://github.com/lepture/authlib/issues/331#issue-838728145

    if not oauth_client:
        raise Exception("No OAuth client")

    metadata = oauth_client.load_server_metadata()
    end_session_endpoint = metadata.get("end_session_endpoint")

    params = dict(id_token_hint=token, post_logout_redirect_uri=redirect_uri)
    encoded_params = urlencode(params)
    end_session_url = f"{end_session_endpoint}?{encoded_params}"

    return redirect(end_session_url)


def _generate_redirect_uri(request, redirect_path):
    redirect_uri = str(request.build_absolute_uri(redirect_path)).lower()

    # this is a temporary hack to ensure redirect URIs are HTTPS when the app is deployed
    # see https://github.com/cal-itp/benefits/issues/442 for more context
    # this follow-up is needed while we address the hosting architecture
    if not redirect_uri.startswith("http://localhost"):
        redirect_uri = redirect_uri.replace("http://", "https://")

    return redirect_uri
