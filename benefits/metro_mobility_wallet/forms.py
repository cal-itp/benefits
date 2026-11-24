from django import forms

from benefits.core.context_processors import formatted_gettext_lazy as _
from benefits.core.mixins import ValidateRecaptchaMixin
from benefits.core.widgets import FormControlEmailInput, FormControlTelInput


class TermsAcceptanceForm(forms.Form):
    """Form to capture acceptance of program terms."""

    action_url = "metro_mobility_wallet:terms"
    id = "form-accept-terms"
    method = "POST"

    accepted_terms = forms.BooleanField(required=True, widget=forms.CheckboxInput())


class ContactInfoConfirmationForm(ValidateRecaptchaMixin, forms.Form):
    """Form to confirm the contact information that the user wants to enroll with."""

    action_url = "metro_mobility_wallet:confirmation"
    id = "form-confirm-info"
    method = "POST"

    submit_value = _("Submit")
    submitting_value = _("Please wait…")
    classes = "confirm-information-form"

    use_custom_validity = True

    blurb = _("Please make sure your email and phone number are correct.")
    email_message = _("Please enter a valid email address. Example: name@example.com.")
    phone_message = _("Please enter a valid U.S. phone number with 10 digits.")

    email = forms.EmailField(
        required=True,
        widget=FormControlEmailInput(),
        error_messages={
            "required": email_message,
            "invalid": email_message,
        },
    )

    # these have to be different because HTML <input> pattern attributes cannot include the ^ and $ assertions
    us_phone_pattern_js = r"(\+1|1)?(\x2D|\(| \()?[2-9]\d{2}(\) |\x2D)?\d{3}\x2D?\d{4}"
    us_phone_pattern_py = rf"^{us_phone_pattern_js}$"

    phone_number = forms.RegexField(
        required=True,
        widget=FormControlTelInput(pattern=us_phone_pattern_js),  # sent to <input> pattern attribute
        regex=us_phone_pattern_py,  # validated by Django
        error_messages={
            "required": phone_message,
            "invalid": phone_message,
        },
    )
