"""
The eligibility application: Form definition for the eligibility verification flow.
"""
from django import forms

from eligibility_verification.core import widgets


class EligibilityVerificationForm(forms.Form):
    submit_value = "Check eligibility"

    last_name = forms.CharField(
        help_text="We use this to confirm your driver license number",
        widget=widgets.FormControlTextInput(placeholder="Your last name")
    )

    pattern = r"[A-Z][0-9]{7}"
    card = forms.RegexField(
        pattern,
        label="CA Driver License or ID Card number",
        error_messages={"invalid": "Enter a valid CA Driver License or ID Card number"},
        widget=widgets.FormControlTextInput(pattern=pattern, placeholder="A1234567")
    )
