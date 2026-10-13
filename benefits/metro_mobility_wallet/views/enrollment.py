from django.views.generic import FormView

from benefits.metro_mobility_wallet.forms import ContactInfoConfirmationForm


class ConfirmationView(FormView):
    template_name = "metro_mobility_wallet/confirmation.html"
    form_class = ContactInfoConfirmationForm
