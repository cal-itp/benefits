"""
The enrollment application: Form definitions for results from Hosted Card Verification Flow.
"""
from django import forms


class CardTokenizeSuccessForm(forms.Form):
    """Form to bring client card token back to server."""

    action_url = "enrollment:index"
    id = "form-card-tokenize-success"
    method = "POST"

    # hidden input with no label
    card_token = forms.CharField(widget=forms.HiddenInput(), label="")


class CardTokenizeFailForm(forms.Form):
    """Form to indicate card tokenization failure to server."""

    id = "form-card-tokenize-fail"
    method = "POST"

    def __init__(self, action_url, *args, **kwargs):
        # init super with an empty data dict
        # binds and makes immutable this form's data
        # since there are no form fields, the form is also marked as valid
        super().__init__({}, *args, **kwargs)
        self.action_url = action_url
