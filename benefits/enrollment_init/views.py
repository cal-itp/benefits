import json
import logging

from django.views.generic import FormView, TemplateView

from benefits.core import models
from benefits.core.mixins import AgencySessionRequiredMixin, EligibleSessionRequiredMixin
from benefits.enrollment import forms
from benefits.enrollment.enrollment import handle_enrollment_results
from benefits.enrollment.views import FlowSessionRequiredMixin
from benefits.enrollment_init.enrollment import enroll

from .routes import routes

logger = logging.getLogger(__name__)


class IndexView(AgencySessionRequiredMixin, EligibleSessionRequiredMixin, FlowSessionRequiredMixin, TemplateView):
    """View for the enrollment landing page."""

    template_name = "enrollment_init/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agency = self.agency

        context.update(
            {
                "cta_button": routes.ENROLLMENT_INIT_REGISTER_CARD,
                "flow": self.flow,
                "transit_processor": {
                    "name": agency.transit_processor_display_name,
                    "website": agency.transit_processor_info_url,
                },
            }
        )
        return context


class RegisterView(AgencySessionRequiredMixin, FlowSessionRequiredMixin, FormView):
    """View for the page that tokenizes the user card."""

    enrollment_method = models.EnrollmentMethods.SELF_SERVICE
    form_class = forms.CardTokenizeSuccessForm
    route_enrollment_success = routes.ENROLLMENT_SUCCESS
    route_reenrollment_error = routes.ENROLLMENT_REENROLLMENT_ERROR
    route_system_error = routes.ENROLLMENT_SYSTEM_ERROR

    route_tokenize_success = routes.ENROLLMENT_INIT_REGISTER_CARD
    template_name = "enrollment_init/register-card.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        tokenize_system_error_form = forms.CardTokenizeFailForm(
            self.route_system_error, "form-card-tokenize-fail-system-error"
        )
        tokenize_success_form = forms.CardTokenizeSuccessForm(
            action_url=self.route_tokenize_success, auto_id=True, label_suffix=""
        )

        context.update(
            {
                "card_schemes": json.dumps(self.agency.supported_card_schemes),
                "collect_js_api_key": self.agency.transit_processor.tokenization_api_key,
                "forms": [tokenize_system_error_form, tokenize_success_form],
                "form_success": tokenize_success_form.id,
                "form_system_error": tokenize_system_error_form.id,
                "success_url": self.route_tokenize_success,
            }
        )
        return context

    def _get_verified_by(self):
        return self.flow.eligibility_verifier

    def form_valid(self, form):
        init_config = self.agency.transit_processor
        flow = self.flow
        group = self.group
        card_token = form.cleaned_data.get("card_token")

        status, exception = enroll(self.request, init_config, flow, group, card_token)

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
