import logging

from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import decorator_from_middleware

from benefits.core import session
from benefits.core.middleware import VerifierSessionRequired
from . import analytics, client, redirects


logger = logging.getLogger(__name__)


ROUTE_AUTH = "oauth:authorize"
ROUTE_START = "eligibility:start"
ROUTE_CONFIRM = "eligibility:confirm"
ROUTE_POST_LOGOUT = "oauth:post_logout"


@decorator_from_middleware(VerifierSessionRequired)
def login(request):
    """View implementing OIDC authorize_redirect."""
    verifier = session.verifier(request)
    oauth_client = client.instance(verifier.auth_scope)

    route = reverse(ROUTE_AUTH)
    redirect_uri = redirects.generate_redirect_uri(request, route)

    logger.debug(f"OAuth authorize_redirect with redirect_uri: {redirect_uri}")

    analytics.started_sign_in(request)

    return oauth_client.authorize_redirect(request, redirect_uri)


def authorize(request):
    """View implementing OIDC token authorization."""
    oauth_client = client.instance()

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
    analytics.started_sign_out(request)

    # overwrite the oauth session token, the user is signed out of the app
    token = session.oauth_token(request)
    session.logout(request)

    route = reverse(ROUTE_POST_LOGOUT)
    redirect_uri = redirects.generate_redirect_uri(request, route)

    logger.debug(f"OAuth end_session_endpoint with redirect_uri: {redirect_uri}")

    # send the user through the end_session_endpoint, redirecting back to
    # the post_logout route
    return redirects.deauthorize_redirect(token, redirect_uri)


def post_logout(request):
    """View routes the user to their origin after sign out."""

    analytics.finished_sign_out(request)

    origin = session.origin(request)
    return redirect(origin)
