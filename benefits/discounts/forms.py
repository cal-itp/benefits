"""
The discounts application: Form definition for results from Hosted Card Verification Flow.
"""
from django import forms


class CardTokenForm(forms.Form):
    """Form to bring client card token back to server."""

    action_url = "discounts:index"
    method = "POST"

    # hidden input with no label
    card_token = forms.CharField(widget=forms.HiddenInput(), label="")
