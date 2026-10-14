from django.views.generic import FormView, TemplateView

from benefits.metro_mobility_wallet.forms import TermsAcceptanceForm


class TermsView(FormView):
    template_name = "metro_mobility_wallet/terms.html"
    form_class = TermsAcceptanceForm


class ApplyView(TemplateView):
    template_name = "metro_mobility_wallet/apply.html"
