"""
The eligibility application: Form definition for the eligibility verification flow.
"""
from django import forms

from eligibility_verification.core import widgets


class EligibilityVerificationForm(forms.Form):
    """Form to collect eligibility verification details."""

    action_url = "eligibility:index"
    method = "POST"

    card = forms.CharField(
        label="CA Driver License or ID Number",
        widget=widgets.FormControlTextInput(placeholder="A1234567")
    )

    last_name = forms.CharField(
        help_text="We use this to confirm your driver license number",
        widget=widgets.FormControlTextInput(placeholder="Your last name")
    )

    submit_value = "Check status"
