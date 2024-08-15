import logging

from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.decorators import decorator_from_middleware
import sentry_sdk

from benefits.routes import routes
from benefits.core import models, session
from benefits.core.middleware import AgencySessionRequired
from . import analytics, redirects
from .client import oauth, create_client
from .middleware import FlowUsesClaimsVerificationSessionRequired


logger = logging.getLogger(__name__)

TEMPLATE_SYSTEM_ERROR = "oauth/system_error.html"


def _oauth_client_or_error_redirect(request, flow: models.EnrollmentFlow):
    """Calls `benefits.oauth.client.create_client()`.

    If a client is created successfully, return it; Otherwise, return a redirect response to OAuth system error.
    """

    oauth_client = None
    exception = None

    try:
        oauth_client = create_client(oauth, flow)
    except Exception as ex:
        exception = ex

    if not oauth_client and not exception:
        exception = Exception(f"oauth_client not registered: {flow.claims_provider.client_name}")

    if exception:
        analytics.error(request, message=str(exception), operation="init")
        sentry_sdk.capture_exception(exception)
        return redirect(routes.OAUTH_SYSTEM_ERROR)

    return oauth_client


@decorator_from_middleware(FlowUsesClaimsVerificationSessionRequired)
def login(request):
    """View implementing OIDC authorize_redirect."""
    flow = session.flow(request)

    oauth_client_result = _oauth_client_or_error_redirect(request, flow)

    if hasattr(oauth_client_result, "authorize_redirect"):
        # this looks like an oauth_client since it has the method we need
        oauth_client = oauth_client_result
    else:
        # this does not look like an oauth_client, it's an error redirect
        return oauth_client_result

    route = reverse(routes.OAUTH_AUTHORIZE)
    redirect_uri = redirects.generate_redirect_uri(request, route)

    logger.debug(f"OAuth authorize_redirect with redirect_uri: {redirect_uri}")

    analytics.started_sign_in(request)
    exception = None
    result = None

    try:
        result = oauth_client.authorize_redirect(request, redirect_uri)
    except Exception as ex:
        exception = ex

    if result and result.status_code >= 400:
        exception = Exception(f"authorize_redirect error response [{result.status_code}]: {result.content.decode()}")
    elif result is None:
        exception = Exception("authorize_redirect returned None")

    if exception:
        analytics.error(request, message=str(exception), operation="authorize_redirect")
        sentry_sdk.capture_exception(exception)
        result = redirect(routes.OAUTH_SYSTEM_ERROR)

    return result


@decorator_from_middleware(FlowUsesClaimsVerificationSessionRequired)
def authorize(request):
    """View implementing OIDC token authorization."""
    flow = session.flow(request)

    oauth_client_result = _oauth_client_or_error_redirect(request, flow)

    if hasattr(oauth_client_result, "authorize_access_token"):
        # this looks like an oauth_client since it has the method we need
        oauth_client = oauth_client_result
    else:
        # this does not look like an oauth_client, it's an error redirect
        return oauth_client_result

    logger.debug("Attempting to authorize OAuth access token")
    token = None
    exception = None

    try:
        token = oauth_client.authorize_access_token(request)
    except Exception as ex:
        exception = ex

    if token is None:
        logger.warning("Could not authorize OAuth access token")
        exception = Exception("oauth_client.authorize_access_token returned None")

    if exception:
        analytics.error(request, message=str(exception), operation="authorize_access_token")
        sentry_sdk.capture_exception(exception)
        return redirect(routes.OAUTH_SYSTEM_ERROR)

    logger.debug("OAuth access token authorized")

    # We store the id_token in the user's session. This is the minimal amount of information needed later to log the user out.
    id_token = token["id_token"]

    # We store the returned claim in case it can be used later in eligibility verification.
    flow_claim = flow.claims_claim
    stored_claim = None

    error_claim = None

    if flow_claim:
        userinfo = token.get("userinfo")

        if userinfo:
            claim_value = userinfo.get(flow_claim)
            # the claim comes back in userinfo like { "claim": "1" | "0" }
            claim_value = int(claim_value) if claim_value else None
            if claim_value is None:
                logger.warning(f"userinfo did not contain: {flow_claim}")
            elif claim_value == 1:
                # if userinfo contains our claim and the flag is 1 (true), store the *claim*
                stored_claim = flow_claim
            elif claim_value >= 10:
                error_claim = claim_value

    session.update(request, oauth_token=id_token, oauth_claim=stored_claim)
    analytics.finished_sign_in(request, error=error_claim)

    return redirect(routes.ELIGIBILITY_CONFIRM)


@decorator_from_middleware(FlowUsesClaimsVerificationSessionRequired)
def cancel(request):
    """View implementing cancellation of OIDC authorization."""

    analytics.canceled_sign_in(request)

    return redirect(routes.ELIGIBILITY_UNVERIFIED)


@decorator_from_middleware(FlowUsesClaimsVerificationSessionRequired)
def logout(request):
    """View implementing OIDC and application sign out."""
    flow = session.flow(request)

    oauth_client_result = _oauth_client_or_error_redirect(request, flow)

    if hasattr(oauth_client_result, "load_server_metadata"):
        # this looks like an oauth_client since it has the method we need
        # (called in redirects.deauthorize_redirect)
        oauth_client = oauth_client_result
    else:
        # this does not look like an oauth_client, it's an error redirect
        return oauth_client_result

    analytics.started_sign_out(request)

    # overwrite the oauth session token, the user is signed out of the app
    token = session.oauth_token(request)
    session.logout(request)

    route = reverse(routes.OAUTH_POST_LOGOUT)
    redirect_uri = redirects.generate_redirect_uri(request, route)

    logger.debug(f"OAuth end_session_endpoint with redirect_uri: {redirect_uri}")

    # send the user through the end_session_endpoint, redirecting back to
    # the post_logout route
    return redirects.deauthorize_redirect(request, oauth_client, token, redirect_uri)


@decorator_from_middleware(FlowUsesClaimsVerificationSessionRequired)
def post_logout(request):
    """View routes the user to their origin after sign out."""

    analytics.finished_sign_out(request)

    origin = session.origin(request)
    return redirect(origin)


@decorator_from_middleware(AgencySessionRequired)
def system_error(request):
    """View handler for an oauth system error."""

    # overwrite origin so that CTA takes user to agency index
    agency = session.agency(request)
    session.update(request, origin=agency.index_url)

    return TemplateResponse(request, TEMPLATE_SYSTEM_ERROR)
