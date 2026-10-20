from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView

from benefits.core.mixins import RecaptchaEnabledMixin
from benefits.metro_mobility_wallet.forms import TermsAcceptanceForm


class TermsView(RecaptchaEnabledMixin, FormView):
    template_name = "metro_mobility_wallet/terms.html"
    form_class = TermsAcceptanceForm

    def form_valid(self, form):
        """If the form is valid, set enrollment flow."""
        return redirect("metro_mobility_wallet:apply")


class ApplyView(TemplateView):
    template_name = "metro_mobility_wallet/apply.html"
