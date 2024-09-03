"""
The enrollment application: view definitions for the benefits enrollment flow.
"""

import logging
from datetime import timedelta

from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import decorator_from_middleware
from littlepay.api.client import Client
from requests.exceptions import HTTPError
import sentry_sdk

from benefits.routes import routes
from benefits.core import session
from benefits.core.middleware import EligibleSessionRequired, FlowSessionRequired, pageview_decorator

from . import analytics, forms

TEMPLATE_RETRY = "enrollment/retry.html"
TEMPLATE_SYSTEM_ERROR = "enrollment/system_error.html"


logger = logging.getLogger(__name__)


@decorator_from_middleware(EligibleSessionRequired)
def token(request):
    """View handler for the enrollment auth token."""
    if not session.enrollment_token_valid(request):
        agency = session.agency(request)

        try:
            client = Client(
                base_url=agency.transit_processor.api_base_url,
                client_id=agency.transit_processor_client_id,
                client_secret=agency.transit_processor_client_secret,
                audience=agency.transit_processor_audience,
            )
            client.oauth.ensure_active_token(client.token)
            response = client.request_card_tokenization_access()
        except Exception as e:
            logger.debug("Error occurred while requesting access token", exc_info=e)
            sentry_sdk.capture_exception(e)

            if isinstance(e, HTTPError):
                status_code = e.response.status_code

                if status_code >= 500:
                    redirect = reverse(routes.ENROLLMENT_SYSTEM_ERROR)
                else:
                    redirect = reverse(routes.SERVER_ERROR)
            else:
                status_code = None
                redirect = reverse(routes.SERVER_ERROR)

            analytics.failed_access_token_request(request, status_code)

            data = {"redirect": redirect}
            return JsonResponse(data)
        else:
            session.update(
                request, enrollment_token=response.get("access_token"), enrollment_token_exp=response.get("expires_at")
            )

    data = {"token": session.enrollment_token(request)}

    return JsonResponse(data)


@decorator_from_middleware(EligibleSessionRequired)
def index(request):
    """View handler for the enrollment landing page."""
    session.update(request, origin=reverse(routes.ENROLLMENT_INDEX))

    agency = session.agency(request)
    flow = session.flow(request)

    # POST back after transit processor form, process card token
    if request.method == "POST":
        form = forms.CardTokenizeSuccessForm(request.POST)
        if not form.is_valid():
            raise Exception("Invalid card token form")

        card_token = form.cleaned_data.get("card_token")

        client = Client(
            base_url=agency.transit_processor.api_base_url,
            client_id=agency.transit_processor_client_id,
            client_secret=agency.transit_processor_client_secret,
            audience=agency.transit_processor_audience,
        )
        client.oauth.ensure_active_token(client.token)

        funding_source = client.get_funding_source_by_token(card_token)
        group_id = flow.group_id

        try:
            group_funding_source = _get_group_funding_source(
                client=client, group_id=group_id, funding_source_id=funding_source.id
            )

            already_enrolled = group_funding_source is not None

            if flow.supports_expiration:
                # set expiry on session
                if already_enrolled and group_funding_source.expiry_date is not None:
                    session.update(request, enrollment_expiry=group_funding_source.expiry_date)
                else:
                    session.update(request, enrollment_expiry=_calculate_expiry(flow.expiration_days))

                if not already_enrolled:
                    # enroll user with an expiration date, return success
                    client.link_concession_group_funding_source(
                        group_id=group_id, funding_source_id=funding_source.id, expiry=session.enrollment_expiry(request)
                    )
                    return success(request)
                else:  # already_enrolled
                    if group_funding_source.expiry_date is None:
                        # update expiration of existing enrollment, return success
                        client.update_concession_group_funding_source_expiry(
                            group_id=group_id,
                            funding_source_id=funding_source.id,
                            expiry=session.enrollment_expiry(request),
                        )
                        return success(request)
                    else:
                        is_expired = _is_expired(group_funding_source.expiry_date)
                        is_within_reenrollment_window = _is_within_reenrollment_window(
                            group_funding_source.expiry_date, session.enrollment_reenrollment(request)
                        )

                        if is_expired or is_within_reenrollment_window:
                            # update expiration of existing enrollment, return success
                            client.update_concession_group_funding_source_expiry(
                                group_id=group_id,
                                funding_source_id=funding_source.id,
                                expiry=session.enrollment_expiry(request),
                            )
                            return success(request)
                        else:
                            # re-enrollment error, return enrollment error with expiration and reenrollment_date
                            return reenrollment_error(request)
            else:  # eligibility does not support expiration
                if not already_enrolled:
                    # enroll user with no expiration date, return success
                    client.link_concession_group_funding_source(group_id=group_id, funding_source_id=funding_source.id)
                    return success(request)
                else:  # already_enrolled
                    if group_funding_source.expiry_date is None:
                        # no action, return success
                        return success(request)
                    else:
                        # remove expiration date, return success
                        raise NotImplementedError("Removing expiration date is currently not supported")

        except HTTPError as e:
            if e.response.status_code >= 500:
                analytics.returned_error(request, str(e))
                sentry_sdk.capture_exception(e)

                return system_error(request)
            else:
                analytics.returned_error(request, str(e))
                raise Exception(f"{e}: {e.response.json()}")
        except Exception as e:
            analytics.returned_error(request, str(e))
            raise e

    # GET enrollment index
    else:
        tokenize_retry_form = forms.CardTokenizeFailForm(routes.ENROLLMENT_RETRY, "form-card-tokenize-fail-retry")
        tokenize_server_error_form = forms.CardTokenizeFailForm(routes.SERVER_ERROR, "form-card-tokenize-fail-server-error")
        tokenize_system_error_form = forms.CardTokenizeFailForm(
            routes.ENROLLMENT_SYSTEM_ERROR, "form-card-tokenize-fail-system-error"
        )
        tokenize_success_form = forms.CardTokenizeSuccessForm(auto_id=True, label_suffix="")

        context = enrollment_get_context(
            request,
            agency,
            tokenize_retry_form=tokenize_retry_form,
            tokenize_server_error_form=tokenize_server_error_form,
            tokenize_system_error_form=tokenize_system_error_form,
            tokenize_success_form=tokenize_success_form,
        )
        logger.debug(f'card_tokenize_url: {context["card_tokenize_url"]}')

        return TemplateResponse(request, flow.enrollment_index_template, context)


def enrollment_get_context(
    request, agency, tokenize_retry_form, tokenize_server_error_form, tokenize_system_error_form, tokenize_success_form
):
    """Returns a context object for the template used for a GET request for the enrollment page."""

    # mapping from Django's I18N LANGUAGE_CODE to Littlepay's overlay language code
    overlay_language = {"en": "en", "es": "es-419"}.get(request.LANGUAGE_CODE, "en")

    context = {
        "forms": [tokenize_retry_form, tokenize_server_error_form, tokenize_system_error_form, tokenize_success_form],
        "cta_button": "tokenize_card",
        "card_tokenize_env": agency.transit_processor.card_tokenize_env,
        "card_tokenize_func": agency.transit_processor.card_tokenize_func,
        "card_tokenize_url": agency.transit_processor.card_tokenize_url,
        "token_field": "card_token",
        "form_retry": tokenize_retry_form.id,
        "form_server_error": tokenize_server_error_form.id,
        "form_success": tokenize_success_form.id,
        "form_system_error": tokenize_system_error_form.id,
        "overlay_language": overlay_language,
    }

    return context


def _get_group_funding_source(client: Client, group_id, funding_source_id):
    group_funding_sources = client.get_concession_group_linked_funding_sources(group_id)
    matching_group_funding_source = None
    for group_funding_source in group_funding_sources:
        if group_funding_source.id == funding_source_id:
            matching_group_funding_source = group_funding_source
            break

    return matching_group_funding_source


def _is_expired(expiry_date):
    """Returns whether the passed in datetime is expired or not."""
    return expiry_date <= timezone.now()


def _is_within_reenrollment_window(expiry_date, enrollment_reenrollment_date):
    """Returns if we are currently within the reenrollment window."""
    return enrollment_reenrollment_date <= timezone.now() < expiry_date


def _calculate_expiry(expiration_days):
    """Returns the expiry datetime, which should be midnight in our configured timezone of the (N + 1)th day from now,
    where N is expiration_days."""
    default_time_zone = timezone.get_default_timezone()
    expiry_date = timezone.localtime(timezone=default_time_zone) + timedelta(days=expiration_days + 1)
    expiry_datetime = expiry_date.replace(hour=0, minute=0, second=0, microsecond=0)

    return expiry_datetime


@decorator_from_middleware(EligibleSessionRequired)
def reenrollment_error(request):
    """View handler for a re-enrollment attempt that is not yet within the re-enrollment window."""
    flow = session.flow(request)

    if flow.reenrollment_error_template is None:
        raise Exception(f"Re-enrollment error with null template on: {flow}")

    if session.logged_in(request) and flow.claims_provider.supports_sign_out:
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

    if session.logged_in(request) and flow.claims_provider.supports_sign_out:
        # overwrite origin for a logged in user
        # if they click the logout button, they are taken to the new route
        session.update(request, origin=reverse(routes.LOGGED_OUT))

    analytics.returned_success(request, flow.group_id)
    context = {"redirect_to": request.path}
    return TemplateResponse(request, flow.enrollment_success_template, context)
