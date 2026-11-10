from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView

from benefits.core.context_processors import formatted_gettext_lazy as _
from benefits.core.mixins import RecaptchaEnabledMixin
from benefits.eligibility.views import CTAButton
from benefits.metro_mobility_wallet.forms import TermsAcceptanceForm
from benefits.metro_mobility_wallet.session import Session


class TermsView(RecaptchaEnabledMixin, FormView):
    template_name = "metro_mobility_wallet/terms.html"
    form_class = TermsAcceptanceForm

    def form_valid(self, form):
        """If the form is valid, user agreed to terms."""
        session = Session(self.request)
        session.accepted_terms = True
        return redirect("metro_mobility_wallet:apply")


class ApplyView(TemplateView):
    template_name = "metro_mobility_wallet/apply.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        apply_context = {
            "call_to_action_button": CTAButton(
                text=_("Apply with"),
                fallback_text="Login.gov",
                route="metro_mobility_wallet:cdt:login",
                extra_classes="login",
            ),
        }

        context.update(apply_context)
        return context
