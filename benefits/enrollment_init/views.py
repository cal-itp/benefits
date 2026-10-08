import logging

from django.http import JsonResponse
from django.views.generic import FormView, TemplateView

from benefits.core.mixins import AgencySessionRequiredMixin, EligibleSessionRequiredMixin
from benefits.enrollment import forms
from benefits.enrollment.views import FlowSessionRequiredMixin

from .routes import routes

logger = logging.getLogger(__name__)


class IndexView(AgencySessionRequiredMixin, EligibleSessionRequiredMixin, FlowSessionRequiredMixin, TemplateView):
    """View for the enrollment landing page."""

    template_name = "enrollment_init/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "cta_button": routes.ENROLLMENT_INIT_REGISTER_CARD,
                "flow": self.flow,
            }
        )
        return context


class RegisterView(AgencySessionRequiredMixin, FlowSessionRequiredMixin, FormView):
    """View for the page that tokenizes the user card."""

    form_class = forms.CardTokenizeSuccessForm

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
                "collect_js_api_key": self.agency.transit_processor.tokenization_api_key,
                "forms": [tokenize_system_error_form, tokenize_success_form],
                "form_success": tokenize_success_form.id,
                "form_system_error": tokenize_system_error_form.id,
                "success_url": self.route_tokenize_success,
            }
        )
        return context

    def form_valid(self, form):
        card_token = form.cleaned_data.get("card_token")
        return JsonResponse({"status": "ok", "tokenized_card": card_token})
