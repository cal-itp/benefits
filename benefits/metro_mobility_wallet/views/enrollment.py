from django.views.generic import FormView, TemplateView

from benefits.metro_mobility_wallet.forms import ContactInfoConfirmationForm


class ConfirmationView(FormView):
    template_name = "metro_mobility_wallet/confirmation.html"
    form_class = ContactInfoConfirmationForm


class SuccessView(TemplateView):
    template_name = "metro_mobility_wallet/success.html"
