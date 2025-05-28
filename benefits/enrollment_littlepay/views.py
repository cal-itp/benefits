import json
import logging

from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse
from django.views.generic import FormView, View
import sentry_sdk

from benefits.routes import routes
from benefits.core import models, session
from benefits.core.mixins import EligibleSessionRequiredMixin

from benefits.enrollment import analytics, forms
from benefits.enrollment.enrollment import Status
from benefits.enrollment_littlepay.enrollment import enroll, request_card_tokenization_access
from benefits.enrollment_littlepay.session import Session

logger = logging.getLogger(__name__)


class TokenView(EligibleSessionRequiredMixin, View):
    """View handler for the card tokenization access token."""

    def get(self, request, *args, **kwargs):
        session = Session(request)

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


class IndexView(EligibleSessionRequiredMixin, FormView):
    template_name = "enrollment_littlepay/index.html"
    form_class = forms.CardTokenizeSuccessForm
    enrollment_result_handler = None

    def get_context_data(self, **kwargs):
        request = self.request
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

        card_types = ["visa", "mastercard"]
        if settings.LITTLEPAY_ADDITIONAL_CARDTYPES:
            card_types.extend(["discover", "amex"])

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
            # convert the python list to a JSON string for use in JavaScript
            "card_types": json.dumps(card_types),
        }

        enrollment_index_context_dict = flow.enrollment_index_context

        match agency.littlepay_config.environment:
            case models.Environment.QA.value:
                url = "https://verify.qa.littlepay.com/assets/js/littlepay.min.js"
                card_tokenize_env = "https://verify.qa.littlepay.com"
            case models.Environment.PROD.value:
                url = "https://verify.littlepay.com/assets/js/littlepay.min.js"
                card_tokenize_env = "https://verify.littlepay.com"
            case _:
                raise ValueError("Unrecognized environment value")

        transit_processor_context = dict(
            name="Littlepay", website="https://littlepay.com", card_tokenize_url=url, card_tokenize_env=card_tokenize_env
        )

        enrollment_index_context_dict["transit_processor"] = transit_processor_context
        context.update(enrollment_index_context_dict)

        return context

    def form_valid(self, form):
        card_token = form.cleaned_data.get("card_token")
        status, exception = enroll(self.request, card_token)

        return self.enrollment_result_handler(self.request, status, exception)

    def form_invalid(self, form):
        raise Exception("Invalid card token form")
