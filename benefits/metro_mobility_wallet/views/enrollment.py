from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView

from benefits.core import recaptcha, session
from benefits.core.context_processors import formatted_gettext_lazy as _
from benefits.core.mixins import EligibleSessionRequiredMixin, RecaptchaEnabledMixin
from benefits.eligibility.views import CTAButton
from benefits.metro_mobility_wallet.forms import ContactInfoConfirmationForm
from benefits.metro_mobility_wallet.mixins import TermsAcceptanceRequiredMixin


class ConfirmationView(EligibleSessionRequiredMixin, TermsAcceptanceRequiredMixin, RecaptchaEnabledMixin, FormView):
    template_name = "metro_mobility_wallet/confirmation.html"
    form_class = ContactInfoConfirmationForm

    def get(self, request, *args, **kwargs):
        email = session.oauth_extra_claims_dict(request)["email"]
        phone = session.oauth_extra_claims_dict(request)["phone_number"]
        phone = phone.removeprefix("+1")
        if len(phone) == 10:
            phone = "{0}-{1}-{2}".format(phone[:3], phone[3:6], phone[6:])

        # sets the `FormView.initial` attribute to pre-fill the fields with the data we got from Login.gov
        self.initial = {
            "email": email,
            "phone_number": phone,
        }
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # store returned name data to output at the top of the page
        first_name = session.oauth_extra_claims_dict(self.request)["given_name"]
        last_name = session.oauth_extra_claims_dict(self.request)["family_name"]

        apply_context = {
            "first_name": first_name,
            "last_name": last_name,
            "call_to_action_button": CTAButton(
                text=_("Submit"),
                route="metro_mobility_wallet:confirmation",
            ),
        }

        context.update(apply_context)
        return context

    def form_valid(self, form):
        """If the form is valid, user agreed to terms."""

        # TODO: Submit info to Submittable via API
        # first_name = session.oauth_extra_claims_dict(self.request)["given_name"]
        # last_name = session.oauth_extra_claims_dict(self.request)["family_name"]

        return redirect("metro_mobility_wallet:success")

    def form_invalid(self, form):
        if recaptcha.has_error(form):
            messages.error(self.request, _("Recaptcha failed. Please try again."))

        return super().form_invalid(form)


class SuccessView(TemplateView):
    template_name = "metro_mobility_wallet/success.html"
