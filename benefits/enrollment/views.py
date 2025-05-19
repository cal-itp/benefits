"""
The enrollment application: view definitions for the benefits enrollment flow.
"""

import logging


from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.decorators import decorator_from_middleware
import sentry_sdk

from benefits.routes import routes
from benefits.core import models, session
from benefits.core.middleware import EligibleSessionRequired, FlowSessionRequired, pageview_decorator

from benefits.enrollment_littlepay.enrollment import request_card_tokenization_access
from benefits.enrollment_littlepay.session import Session as LittlepaySession
from benefits.enrollment_littlepay.views import IndexView as LittlepayIndexView
from . import analytics
from .enrollment import Status

TEMPLATE_RETRY = "enrollment/retry.html"
TEMPLATE_SYSTEM_ERROR = "enrollment/system_error.html"


logger = logging.getLogger(__name__)


@decorator_from_middleware(EligibleSessionRequired)
def token(request):
    """View handler for the enrollment auth token."""
    session = LittlepaySession(request)

    if not session.access_token_valid():
        response = request_card_tokenization_access(request)

        if response.status is Status.SUCCESS:
            session.access_token = response.access_token
            session.access_token_expiry = response.expires_at
        elif response.status is Status.SYSTEM_ERROR or response.status is Status.EXCEPTION:
            logger.debug("Error occurred while requesting access token", exc_info=response.exception)
            sentry_sdk.capture_exception(response.exception)
            analytics.failed_access_token_request(request, response.status_code)

            if response.status is Status.SYSTEM_ERROR:
                redirect = reverse(routes.ENROLLMENT_SYSTEM_ERROR)
            else:
                redirect = reverse(routes.SERVER_ERROR)

            data = {"redirect": redirect}
            return JsonResponse(data)

    data = {"token": session.access_token}

    return JsonResponse(data)


@decorator_from_middleware(EligibleSessionRequired)
def index(request):
    """View handler for the enrollment landing page."""
    session.update(request, origin=reverse(routes.ENROLLMENT_INDEX))

    return LittlepayIndexView.as_view(enrollment_result_handler=_enrollment_result_handler)(request)


def _enrollment_result_handler(request, status: Status, exception: Exception):
    match (status):
        case Status.SUCCESS:
            agency = session.agency(request)
            flow = session.flow(request)
            expiry = session.enrollment_expiry(request)
            oauth_extra_claims = session.oauth_extra_claims(request)
            # EnrollmentEvent expects a string value for extra_claims
            if oauth_extra_claims:
                str_extra_claims = ", ".join(oauth_extra_claims)
            else:
                str_extra_claims = ""
            event = models.EnrollmentEvent.objects.create(
                transit_agency=agency,
                enrollment_flow=flow,
                enrollment_method=models.EnrollmentMethods.DIGITAL,
                verified_by=flow.eligibility_verifier,
                expiration_datetime=expiry,
                extra_claims=str_extra_claims,
            )
            event.save()
            analytics.returned_success(request, flow.group_id, extra_claims=oauth_extra_claims)
            return success(request)

        case Status.SYSTEM_ERROR:
            analytics.returned_error(request, str(exception))
            sentry_sdk.capture_exception(exception)
            return system_error(request)

        case Status.EXCEPTION:
            analytics.returned_error(request, str(exception))
            raise exception

        case Status.REENROLLMENT_ERROR:
            return reenrollment_error(request)


@decorator_from_middleware(EligibleSessionRequired)
def reenrollment_error(request):
    """View handler for a re-enrollment attempt that is not yet within the re-enrollment window."""
    flow = session.flow(request)

    if not flow.reenrollment_error_template:
        raise Exception(f"Re-enrollment error with null template on: {flow}")

    if session.logged_in(request) and flow.supports_sign_out:
        # overwrite origin for a logged in user
        # if they click the logout button, they are taken to the new route
        session.update(request, origin=reverse(routes.LOGGED_OUT))

    analytics.returned_error(request, "Re-enrollment error.")

    return TemplateResponse(request, flow.reenrollment_error_template)


@decorator_from_middleware(EligibleSessionRequired)
def retry(request):
    """View handler for a recoverable failure condition."""
    analytics.returned_retry(request)
    return TemplateResponse(request, TEMPLATE_RETRY)


@decorator_from_middleware(EligibleSessionRequired)
def system_error(request):
    """View handler for an enrollment system error."""

    # overwrite origin so that CTA takes user to agency index
    agency = session.agency(request)
    session.update(request, origin=agency.index_url)

    return TemplateResponse(request, TEMPLATE_SYSTEM_ERROR)


@pageview_decorator
@decorator_from_middleware(EligibleSessionRequired)
@decorator_from_middleware(FlowSessionRequired)
def success(request):
    """View handler for the final success page."""
    request.path = "/enrollment/success"
    session.update(request, origin=reverse(routes.ENROLLMENT_SUCCESS))

    flow = session.flow(request)

    if session.logged_in(request) and flow.supports_sign_out:
        # overwrite origin for a logged in user
        # if they click the logout button, they are taken to the new route
        session.update(request, origin=reverse(routes.LOGGED_OUT))

    context = {"redirect_to": request.path}
    context.update(flow.enrollment_success_context)

    return TemplateResponse(request, "enrollment/success.html", context)
