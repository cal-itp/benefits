import logging

from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import decorator_from_middleware

from benefits.core import session
from benefits.core.middleware import VerifierSessionRequired
from . import analytics, redirects
from .client import oauth


logger = logging.getLogger(__name__)


ROUTE_AUTH = "oauth:authorize"
ROUTE_START = "eligibility:start"
ROUTE_CONFIRM = "eligibility:confirm"
ROUTE_UNVERIFIED = "eligibility:unverified"
ROUTE_POST_LOGOUT = "oauth:post_logout"


@decorator_from_middleware(VerifierSessionRequired)
def login(request):
    """View implementing OIDC authorize_redirect."""
    verifier = session.verifier(request)
    oauth_client = oauth.create_client(verifier.auth_provider.client_name)

    if not oauth_client:
        raise Exception(f"oauth_client not registered: {verifier.auth_provider.client_name}")

    route = reverse(ROUTE_AUTH)
    redirect_uri = redirects.generate_redirect_uri(request, route)

    logger.debug(f"OAuth authorize_redirect with redirect_uri: {redirect_uri}")

    analytics.started_sign_in(request)

    return oauth_client.authorize_redirect(request, redirect_uri)


@decorator_from_middleware(VerifierSessionRequired)
def authorize(request):
    """View implementing OIDC token authorization."""
    verifier = session.verifier(request)
    oauth_client = oauth.create_client(verifier.auth_provider.client_name)

    if not oauth_client:
        raise Exception(f"oauth_client not registered: {verifier.auth_provider.client_name}")

    logger.debug("Attempting to authorize OAuth access token")
    token = oauth_client.authorize_access_token(request)

    if token is None:
        logger.warning("Could not authorize OAuth access token")
        return redirect(ROUTE_START)

    logger.debug("OAuth access token authorized")

    # We store the id_token in the user's session. This is the minimal amount of information needed later to log the user out.
    id_token = token["id_token"]

    # We store the returned claim in case it can be used later in eligibility verification.
    verifier_claim = verifier.auth_provider.claim
    stored_claim = None

    if verifier_claim:
        userinfo = token.get("userinfo")

        if userinfo:
            claim_value = userinfo.get(verifier_claim)
            # the claim comes back in userinfo like { "claim": "True" | "False" }
            if claim_value is None:
                logger.warning(f"userinfo did not contain: {verifier_claim}")
            elif claim_value.lower() == "true":
                # if userinfo contains our claim and the flag is true, store the *claim*
                stored_claim = verifier_claim

    session.update(request, oauth_token=id_token, oauth_claim=stored_claim)

    analytics.finished_sign_in(request)

    return redirect(ROUTE_CONFIRM)


@decorator_from_middleware(VerifierSessionRequired)
def cancel(request):
    """View implementing cancellation of OIDC authorization."""

    analytics.canceled_sign_in(request)

    return redirect(ROUTE_UNVERIFIED)


@decorator_from_middleware(VerifierSessionRequired)
def logout(request):
    """View implementing OIDC and application sign out."""
    verifier = session.verifier(request)
    oauth_client = oauth.create_client(verifier.auth_provider.client_name)

    if not oauth_client:
        raise Exception(f"oauth_client not registered: {verifier.auth_provider.client_name}")

    analytics.started_sign_out(request)

    # overwrite the oauth session token, the user is signed out of the app
    token = session.oauth_token(request)
    session.logout(request)

    route = reverse(ROUTE_POST_LOGOUT)
    redirect_uri = redirects.generate_redirect_uri(request, route)

    logger.debug(f"OAuth end_session_endpoint with redirect_uri: {redirect_uri}")

    # send the user through the end_session_endpoint, redirecting back to
    # the post_logout route
    return redirects.deauthorize_redirect(oauth_client, token, redirect_uri)


@decorator_from_middleware(VerifierSessionRequired)
def post_logout(request):
    """View routes the user to their origin after sign out."""

    analytics.finished_sign_out(request)

    origin = session.origin(request)
    return redirect(origin)
