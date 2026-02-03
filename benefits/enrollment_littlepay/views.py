import json
import logging

import sentry_sdk
from django.http import JsonResponse
from django.urls import reverse
from django.views.generic import FormView, View

from benefits.core import models
from benefits.core.mixins import AgencySessionRequiredMixin, EligibleSessionRequiredMixin, FlowSessionRequiredMixin
from benefits.enrollment import analytics, forms
from benefits.enrollment.enrollment import Status, handle_enrollment_results
from benefits.enrollment_littlepay.enrollment import enroll, request_card_tokenization_access
from benefits.enrollment_littlepay.session import Session
from benefits.routes import routes

logger = logging.getLogger(__name__)


class TokenView(EligibleSessionRequiredMixin, View):
    """View handler for the card tokenization access token."""

    enrollment_method = models.EnrollmentMethods.DIGITAL
    route_system_error = routes.ENROLLMENT_SYSTEM_ERROR
    route_server_error = routes.SERVER_ERROR

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
                analytics.failed_pretokenization_request(request, "littlepay", response.status_code, self.enrollment_method)

                if response.status is Status.SYSTEM_ERROR:
                    redirect = reverse(self.route_system_error)
                else:
                    redirect = reverse(self.route_server_error)

                data = {"redirect": redirect}
                return JsonResponse(data)

        data = {"token": session.access_token}
        return JsonResponse(data)


class IndexView(AgencySessionRequiredMixin, FlowSessionRequiredMixin, EligibleSessionRequiredMixin, FormView):
    """View for the enrollment landing page."""

    enrollment_method = models.EnrollmentMethods.DIGITAL
    form_class = forms.CardTokenizeSuccessForm
    route_enrollment_success = routes.ENROLLMENT_SUCCESS
    route_enrollment_retry = routes.ENROLLMENT_RETRY
    route_reenrollment_error = routes.ENROLLMENT_REENROLLMENT_ERROR
    route_server_error = routes.SERVER_ERROR
    route_system_error = routes.ENROLLMENT_SYSTEM_ERROR
    route_tokenize_success = routes.ENROLLMENT_LITTLEPAY_INDEX
    template_name = "enrollment_littlepay/index.html"

    def get_context_data(self, **kwargs):
        request = self.request
        agency = self.agency
        flow = self.flow

        tokenize_retry_form = forms.CardTokenizeFailForm(self.route_enrollment_retry, "form-card-tokenize-fail-retry")
        tokenize_server_error_form = forms.CardTokenizeFailForm(
            self.route_server_error, "form-card-tokenize-fail-server-error"
        )
        tokenize_system_error_form = forms.CardTokenizeFailForm(
            self.route_system_error, "form-card-tokenize-fail-system-error"
        )
        tokenize_success_form = forms.CardTokenizeSuccessForm(
            action_url=self.route_tokenize_success, auto_id=True, label_suffix=""
        )

        context = {
            "forms": [tokenize_retry_form, tokenize_server_error_form, tokenize_system_error_form, tokenize_success_form],
            "cta_button": "tokenize_card",
            "enrollment_method": self.enrollment_method,
            "token_field": "card_token",
            "form_retry": tokenize_retry_form.id,
            "form_server_error": tokenize_server_error_form.id,
            "form_success": tokenize_success_form.id,
            "form_system_error": tokenize_system_error_form.id,
            "overlay_language": self._get_overlay_language(request.LANGUAGE_CODE),
            "card_schemes": json.dumps(agency.supported_card_schemes),
        }

        enrollment_index_context_dict = flow.enrollment_index_context

        match agency.littlepay_config.environment:
            case models.Environment.TEST.value:
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

    def _get_overlay_language(self, django_language_code):
        """Given a Django language code, return the corresponding language code to use with Littlepay's overlay."""
        # mapping from Django's I18N LANGUAGE_CODE to Littlepay's overlay language code
        overlay_language = {"en": "en", "es": "es-419"}.get(django_language_code, "en")
        return overlay_language

    def _get_verified_by(self):
        return self.flow.eligibility_verifier

    def form_valid(self, form):
        card_token = form.cleaned_data.get("card_token")
        status, exception, funding_source = enroll(self.request, card_token)

        return handle_enrollment_results(
            request=self.request,
            status=status,
            verified_by=self._get_verified_by(),
            exception=exception,
            enrollment_method=self.enrollment_method,
            route_reenrollment_error=self.route_reenrollment_error,
            route_success=self.route_enrollment_success,
            route_system_error=self.route_system_error,
            card_category=funding_source.card_category,
            card_scheme=funding_source.card_scheme,
        )

    def form_invalid(self, form):
        raise Exception("Invalid card token form")
