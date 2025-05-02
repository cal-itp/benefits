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
from benefits.core import session
from benefits.core.middleware import AgencySessionRequired, EligibleSessionRequired, FlowSessionRequired, pageview_decorator

from benefits.core import models
from . import analytics, forms
from .enrollment import Status, LittlepayEnrollment, SwitchioEnrollment

TEMPLATE_RETRY = "enrollment/retry.html"
TEMPLATE_SYSTEM_ERROR = "enrollment/system_error.html"


logger = logging.getLogger(__name__)


def _get_enrollment_class(agency: models.TransitAgency):
    if agency.littlepay_config:
        return LittlepayEnrollment
    elif agency.switchio_config:
        return SwitchioEnrollment
    else:
        raise ValueError("Transit agency does not have a Littlepay or Switchio config")


@decorator_from_middleware(AgencySessionRequired)
@decorator_from_middleware(EligibleSessionRequired)
def token(request):
    """View handler for the enrollment auth token."""
    agency = session.agency(request)
    enrollment = _get_enrollment_class(agency)()

    response, data = enrollment.initiate_tokenization(request)

    if response.status is Status.SYSTEM_ERROR or response.status is Status.EXCEPTION:
        logger.debug("Error occurred while initiating tokenization", exc_info=response.exception)
        sentry_sdk.capture_exception(response.exception)
        analytics.failed_access_token_request(request, response.status_code)

        if response.status is Status.SYSTEM_ERROR:
            redirect = reverse(routes.ENROLLMENT_SYSTEM_ERROR)
        else:
            redirect = reverse(routes.SERVER_ERROR)

        data = {"redirect": redirect}

    return JsonResponse(data)


@decorator_from_middleware(AgencySessionRequired)
@decorator_from_middleware(EligibleSessionRequired)
def index(request):
    """View handler for the enrollment landing page."""
    session.update(request, origin=reverse(routes.ENROLLMENT_INDEX))

    agency = session.agency(request)
    enrollment = _get_enrollment_class(agency)()

    # this is what we have to do until we introduce separate Django apps that have littlepay and switchio views
    if isinstance(enrollment, LittlepayEnrollment):
        return _index_for_littlepay(request, enrollment)
    else:  # is instance of SwitchioEnrollment
        return _index_for_switchio(request, enrollment)


def _index_for_littlepay(request, enrollment):
    # POST back after transit processor form, process card token
    if request.method == "POST":
        form = forms.CardTokenizeSuccessForm(request.POST)
        if not form.is_valid():
            raise Exception("Invalid card token form")

        card_token = form.cleaned_data.get("card_token")
        status, exception = enrollment.enroll(request, card_token)

        return _handle_enrollment_results(request, status, exception)

    # GET enrollment index
    else:
        agency = session.agency(request)
        flow = session.flow(request)

        tokenize_retry_form = forms.CardTokenizeFailForm(routes.ENROLLMENT_RETRY, "form-card-tokenize-fail-retry")
        tokenize_server_error_form = forms.CardTokenizeFailForm(routes.SERVER_ERROR, "form-card-tokenize-fail-server-error")
        tokenize_system_error_form = forms.CardTokenizeFailForm(
            routes.ENROLLMENT_SYSTEM_ERROR, "form-card-tokenize-fail-system-error"
        )
        tokenize_success_form = forms.CardTokenizeSuccessForm(
            action_url=routes.ENROLLMENT_INDEX, auto_id=True, label_suffix=""
        )

        # mapping from Django's I18N LANGUAGE_CODE to Littlepay's overlay language code
        overlay_language = {"en": "en", "es": "es-419"}.get(request.LANGUAGE_CODE, "en")

        context = {
            "forms": [tokenize_retry_form, tokenize_server_error_form, tokenize_system_error_form, tokenize_success_form],
            "cta_button": "tokenize_card",
            "enrollment_method": models.EnrollmentMethods.DIGITAL,
            "token_field": "card_token",
            "form_retry": tokenize_retry_form.id,
            "form_server_error": tokenize_server_error_form.id,
            "form_success": tokenize_success_form.id,
            "form_system_error": tokenize_system_error_form.id,
            "overlay_language": overlay_language,
        }
        context.update(flow.enrollment_index_context)

        return TemplateResponse(request, agency.enrollment_index_template, context)


def _index_for_switchio(request, enrollment):
    agency = session.agency(request)
    flow = session.flow(request)

    context = {
        "cta_button": "tokenize_card",
        "enrollment_method": models.EnrollmentMethods.DIGITAL,
    }
    context.update(flow.enrollment_index_context)

    return TemplateResponse(request, agency.enrollment_index_template, context)


def _handle_enrollment_results(request, status, exception):
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
