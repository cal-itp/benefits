"""
The eligibility application: Form definition for the eligibility verification flow.
"""
from django import forms

from eligibility_verification.core import widgets


class EligibilityVerificationForm(forms.Form):
    """Form to collect eligibility verification details."""

    action_url = "eligibility:verify"
    method = "POST"

    card = forms.CharField(
        label="CA Driver License or ID Number",
        widget=widgets.FormControlTextInput(placeholder="A1234567")
    )

    last_name = forms.CharField(
        label="Last Name (as it appears on ID)",
        widget=widgets.FormControlTextInput(placeholder="Rodriguez")
    )

    submit_value = "Check status"
    submitting_value = "Checking"
