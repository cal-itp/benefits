"""
The enrollment application: view definitions for the benefits enrollment flow.
"""

import logging

from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.decorators import decorator_from_middleware
from littlepay.api.client import Client
from requests.exceptions import HTTPError

from benefits.core import session
from benefits.core.middleware import (
    EligibleSessionRequired,
    VerifierSessionRequired,
    pageview_decorator,
)
from benefits.core.views import ROUTE_LOGGED_OUT
from . import analytics, forms


ROUTE_INDEX = "enrollment:index"
ROUTE_RETRY = "enrollment:retry"
ROUTE_SUCCESS = "enrollment:success"
ROUTE_TOKEN = "enrollment:token"

TEMPLATE_RETRY = "enrollment/retry.html"
TEMPLATE_SUCCESS = "enrollment/success.html"


logger = logging.getLogger(__name__)


@decorator_from_middleware(EligibleSessionRequired)
def token(request):
    """View handler for the enrollment auth token."""
    if not session.enrollment_token_valid(request):
        agency = session.agency(request)
        payment_processor = agency.payment_processor
        client = Client(
            base_url=payment_processor.api_base_url,
            client_id=payment_processor.client_id,
            client_secret=payment_processor.client_secret,
            audience=payment_processor.audience,
        )
        client.oauth.ensure_active_token(client.token)
        response = client.request_card_tokenization_access()
        session.update(request, enrollment_token=response.get("access_token"), enrollment_token_exp=response.get("expires_at"))

    data = {"token": session.enrollment_token(request)}

    return JsonResponse(data)


@decorator_from_middleware(EligibleSessionRequired)
def index(request):
    """View handler for the enrollment landing page."""
    session.update(request, origin=reverse(ROUTE_INDEX))

    agency = session.agency(request)
    eligibility = session.eligibility(request)
    payment_processor = agency.payment_processor

    # POST back after payment processor form, process card token
    if request.method == "POST":
        form = forms.CardTokenizeSuccessForm(request.POST)
        if not form.is_valid():
            raise Exception("Invalid card token form")

        logger.debug("Read tokenized card")
        card_token = form.cleaned_data.get("card_token")

        client = Client(
            base_url=payment_processor.api_base_url,
            client_id=payment_processor.client_id,
            client_secret=payment_processor.client_secret,
            audience=payment_processor.audience,
        )
        client.oauth.ensure_active_token(client.token)

        funding_source = client.get_funding_source_by_token(card_token)
        group_id = eligibility.group_id

        try:
            group_funding_source = _get_group_funding_source(
                client=client, group_id=group_id, funding_source_id=funding_source.id
            )

            already_enrolled = group_funding_source is not None

            if not already_enrolled:
                # enroll user with no expiration date, return success
                client.link_concession_group_funding_source(group_id=group_id, funding_source_id=funding_source.id)
                return _success(request, group_id)
            else:
                # no action, return success
                return _success(request, group_id)

        except HTTPError as e:
            analytics.returned_error(request, str(e))
            raise Exception(f"{e}: {e.response.json()}")
        except Exception as e:
            analytics.returned_error(request, str(e))
            raise e

    # GET enrollment index
    else:
        tokenize_retry_form = forms.CardTokenizeFailForm(ROUTE_RETRY)
        tokenize_success_form = forms.CardTokenizeSuccessForm(auto_id=True, label_suffix="")

        context = {
            "forms": [tokenize_retry_form, tokenize_success_form],
            "cta_button": "tokenize_card",
            "card_tokenize_env": agency.payment_processor.card_tokenize_env,
            "card_tokenize_func": agency.payment_processor.card_tokenize_func,
            "card_tokenize_url": agency.payment_processor.card_tokenize_url,
            "token_field": "card_token",
            "form_retry": tokenize_retry_form.id,
            "form_success": tokenize_success_form.id,
        }

        logger.debug(f'card_tokenize_url: {context["card_tokenize_url"]}')

        return TemplateResponse(request, eligibility.enrollment_index_template, context)


def _success(request, group_id):
    analytics.returned_success(request, group_id)
    return success(request)


def _get_group_funding_source(client: Client, group_id, funding_source_id):
    group_funding_sources = client.get_concession_group_linked_funding_sources(group_id)
    matching_group_funding_source = None
    for group_funding_source in group_funding_sources:
        if group_funding_source.id == funding_source_id:
            matching_group_funding_source = group_funding_source
            break

    return matching_group_funding_source


@decorator_from_middleware(EligibleSessionRequired)
def retry(request):
    """View handler for a recoverable failure condition."""
    if request.method == "POST":
        analytics.returned_retry(request)
        form = forms.CardTokenizeFailForm(request.POST)
        if form.is_valid():
            return TemplateResponse(request, TEMPLATE_RETRY)
        else:
            analytics.returned_error(request, "Invalid retry submission.")
            raise Exception("Invalid retry submission.")
    else:
        analytics.returned_error(request, "This view method only supports POST.")
        raise Exception("This view method only supports POST.")


@pageview_decorator
@decorator_from_middleware(VerifierSessionRequired)
def success(request):
    """View handler for the final success page."""
    request.path = "/enrollment/success"
    session.update(request, origin=reverse(ROUTE_SUCCESS))

    agency = session.agency(request)
    verifier = session.verifier(request)

    if session.logged_in(request) and verifier.auth_provider.supports_sign_out:
        # overwrite origin for a logged in user
        # if they click the logout button, they are taken to the new route
        session.update(request, origin=reverse(ROUTE_LOGGED_OUT))

    return TemplateResponse(request, agency.enrollment_success_template)
