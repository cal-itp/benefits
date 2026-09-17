import logging

from django.views.generic import FormView

from benefits.core import models
from benefits.core.context_processors import formatted_gettext_lazy as _
from benefits.core.mixins import AgencySessionRequiredMixin
from benefits.enrollment import forms
from benefits.enrollment.views import IndexContextMixin
from benefits.routes import routes

logger = logging.getLogger(__name__)


# EligibleSessionRequiredMixin
class IndexView(AgencySessionRequiredMixin, IndexContextMixin, FormView):
    """View for the enrollment landing page."""

    enrollment_method = models.EnrollmentMethods.SELF_SERVICE
    template_name = "enrollment_init/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "headline": _("You are eligible for a reduced fare!"),
                "next_step": _("The last step is to register a bank card so you get a reduced fare when you tap."),
                "collect_js_api_key": self.agency.init_config.tokenization_api_key,
                "cta_button": routes.ENROLLMENT_INIT_START,
                "enrollment_method": self.enrollment_method,
                "flow": self.flow,
                "transit_processor": {
                    "name": "INIT",
                    "website": "https://www.initse.com/enus/solutions/fare-collection-revenue-management/",
                },
            }
        )
        return context


class StartView(AgencySessionRequiredMixin, IndexContextMixin, FormView):
    """View for the page that tokenizes the user card."""

    enrollment_method = models.EnrollmentMethods.SELF_SERVICE
    form_class = forms.CardTokenizeSuccessForm
    route_enrollment_success = routes.ENROLLMENT_SUCCESS
    route_reenrollment_error = routes.ENROLLMENT_REENROLLMENT_ERROR
    route_retry = routes.ENROLLMENT_RETRY
    route_system_error = routes.ENROLLMENT_SYSTEM_ERROR
    route_server_error = routes.SERVER_ERROR
    route_tokenize_success = routes.ENROLLMENT_INIT_SUCCESS
    template_name = "enrollment_init/start.html"

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
                "collect_js_api_key": self.agency.init_config.tokenization_api_key,
                "forms": [tokenize_system_error_form, tokenize_success_form],
                "form_success": tokenize_success_form.id,
                "form_system_error": tokenize_system_error_form.id,
                "success_url": self.route_tokenize_success,
                "enrollment_method": self.enrollment_method,
                "transit_processor": {
                    "name": "INIT",
                    "website": "https://www.initse.com/enus/solutions/fare-collection-revenue-management/",
                },
            }
        )
        return context


class SuccessView(AgencySessionRequiredMixin, IndexContextMixin, FormView):
    """View for the page that tokenizes the user card."""

    template_name = "enrollment_init/success.html"
