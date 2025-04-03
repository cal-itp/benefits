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
        exception = Exception(f"oauth_client not registered: {flow.oauth_config.client_name}")

    if exception:
        analytics.error(request, message=str(exception), operation="init")
        sentry_sdk.capture_exception(exception)
        return redirect(routes.OAUTH_SYSTEM_ERROR)

    return oauth_client


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

    # the user is signed out of the app
    session.logout(request)

    route = reverse(routes.OAUTH_POST_LOGOUT)
    redirect_uri = redirects.generate_redirect_uri(request, route)

    logger.debug(f"OAuth end_session_endpoint with redirect_uri: {redirect_uri}")

    # send the user through the end_session_endpoint, redirecting back to
    # the post_logout route
    return redirects.deauthorize_redirect(request, oauth_client, redirect_uri)


@decorator_from_middleware(AgencySessionRequired)
def system_error(request):
    """View handler for an oauth system error."""

    # overwrite origin so that CTA takes user to agency index
    agency = session.agency(request)
    session.update(request, origin=agency.index_url)

    return TemplateResponse(request, TEMPLATE_SYSTEM_ERROR)
