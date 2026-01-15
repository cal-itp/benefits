import logging

import sentry_sdk
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import FormView, View

from benefits.core import models
from benefits.core.mixins import AgencySessionRequiredMixin, EligibleSessionRequiredMixin, FlowSessionRequiredMixin
from benefits.enrollment import analytics, forms
from benefits.enrollment.enrollment import Status, handle_enrollment_results
from benefits.enrollment_switchio.enrollment import (
    enroll,
    get_latest_active_token_value,
    get_registration_status,
    request_registration,
)
from benefits.enrollment_switchio.models import SwitchioConfig
from benefits.enrollment_switchio.session import Session
from benefits.routes import routes

logger = logging.getLogger(__name__)


class IndexView(AgencySessionRequiredMixin, FlowSessionRequiredMixin, EligibleSessionRequiredMixin, FormView):
    """View for the enrollment landing page."""

    enrollment_method = models.EnrollmentMethods.DIGITAL
    form_class = forms.CardTokenizeSuccessForm
    route_enrollment_success = routes.ENROLLMENT_SUCCESS
    route_reenrollment_error = routes.ENROLLMENT_REENROLLMENT_ERROR
    route_retry = routes.ENROLLMENT_RETRY
    route_system_error = routes.ENROLLMENT_SYSTEM_ERROR
    route_server_error = routes.SERVER_ERROR
    route_tokenize_success = routes.ENROLLMENT_SWITCHIO_INDEX
    template_name = "enrollment_switchio/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        request = self.request
        flow = self.flow

        tokenize_system_error_form = forms.CardTokenizeFailForm(
            self.route_system_error, "form-card-tokenize-fail-system-error"
        )
        tokenize_success_form = forms.CardTokenizeSuccessForm(
            action_url=self.route_tokenize_success, auto_id=True, label_suffix=""
        )
        context.update(
            {
                **flow.enrollment_index_context,
                "forms": [tokenize_system_error_form, tokenize_success_form],
                "form_success": tokenize_success_form.id,
                "form_system_error": tokenize_system_error_form.id,
                "cta_button": "tokenize_card",
                "enrollment_method": self.enrollment_method,
                "transit_processor": {"name": "Switchio", "website": "https://switchio.com/transport/"},
                "locale": self._get_locale(request.LANGUAGE_CODE),
            }
        )
        return context

    def _get_locale(self, django_language_code):
        """Given a Django language code, return the corresponding locale to use with Switchio's tokenization gateway."""
        # mapping from Django's I18N LANGUAGE_CODE to Switchio's locales
        locale = {"en": "en", "es": "es"}.get(django_language_code, "en")
        return locale

    def _get_verified_by(self):
        return self.flow.eligibility_verifier

    def get(self, request: HttpRequest, *args, **kwargs):
        session = Session(request)
        switchio_config = self.agency.switchio_config

        if session.registration_id:
            response = get_registration_status(switchio_config=switchio_config, registration_id=session.registration_id)
            if response.status is Status.SUCCESS:
                reg_state = response.registration_status.regState
                if reg_state == "tokenization_finished":
                    # give card token to index template so it can send
                    # "finished card tokenization" event and POST either the
                    # CardTokenizeSuccessForm or CardTokenizeFailForm.
                    context_data = self.get_context_data(**kwargs)

                    context_data["card_token"] = get_latest_active_token_value(response.registration_status.tokens)
                    return self.render_to_response(context=context_data)
                elif reg_state == "verification_failed":
                    return redirect(self.route_retry)
                elif reg_state == "tokenization_failed":
                    sentry_sdk.capture_exception(Exception("Tokenization failed"))
                    return redirect(self.route_system_error)
            else:
                sentry_sdk.capture_exception(response.exception)

                if response.status is Status.SYSTEM_ERROR:
                    return redirect(self.route_system_error)
                elif response.status is Status.EXCEPTION:
                    return redirect(self.route_server_error)

        return super().get(request=request, *args, **kwargs)

    def form_valid(self, form):
        switchio_config = self.agency.switchio_config
        flow = self.flow
        card_token = form.cleaned_data.get("card_token")

        status, exception = enroll(request=self.request, switchio_config=switchio_config, flow=flow, token=card_token)
        return handle_enrollment_results(
            request=self.request,
            status=status,
            verified_by=self._get_verified_by(),
            exception=exception,
            enrollment_method=self.enrollment_method,
            route_reenrollment_error=self.route_reenrollment_error,
            route_success=self.route_enrollment_success,
            route_system_error=self.route_system_error,
        )


class GatewayUrlView(AgencySessionRequiredMixin, EligibleSessionRequiredMixin, View):
    """View for the tokenization gateway registration"""

    enrollment_method = models.EnrollmentMethods.DIGITAL
    route_redirect = routes.ENROLLMENT_SWITCHIO_INDEX
    route_system_error = routes.ENROLLMENT_SYSTEM_ERROR
    route_server_error = routes.SERVER_ERROR

    def get(self, request: HttpRequest, *args, **kwargs):
        session = Session(request)
        switchio_config = self.agency.switchio_config

        if session.registration_id is None or session.gateway_url is None:
            return self._request_registration(request, switchio_config, session)
        else:
            response = get_registration_status(switchio_config=switchio_config, registration_id=session.registration_id)

            if response.status is Status.SUCCESS:
                # if the registration session is no longer valid, request a new registration session.
                if response.registration_status.regState in ["expired", "deleted"]:
                    return self._request_registration(request, switchio_config, session)
                else:
                    return self._gateway_url_response(session)
            else:
                logger.debug(f"Error occurred while attempting to get registration status for {session.registration_id}")
                sentry_sdk.capture_exception(response.exception)
                analytics.failed_pretokenization_request(request, "switchio", response.status_code, self.enrollment_method)

                if response.status is Status.SYSTEM_ERROR:
                    redirect = reverse(self.route_system_error)
                else:
                    redirect = reverse(self.route_server_error)

                data = {"redirect": redirect}
                return JsonResponse(data)

    def _request_registration(self, request: HttpRequest, switchio_config: SwitchioConfig, session: Session) -> JsonResponse:
        response = request_registration(request, switchio_config, self.route_redirect)

        if response.status is Status.SUCCESS:
            registration = response.registration
            session.registration_id = registration.regId
            session.gateway_url = registration.gtwUrl

            return self._gateway_url_response(session)
        else:
            logger.debug("Error occurred while requesting a tokenization gateway registration", exc_info=response.exception)
            sentry_sdk.capture_exception(response.exception)
            analytics.failed_pretokenization_request(request, "switchio", response.status_code, self.enrollment_method)

            if response.status is Status.SYSTEM_ERROR:
                redirect = reverse(self.route_system_error)
            else:
                redirect = reverse(self.route_server_error)

            data = {"redirect": redirect}
            return JsonResponse(data)

    def _gateway_url_response(self, session: Session):
        data = {"gateway_url": session.gateway_url}
        return JsonResponse(data)
