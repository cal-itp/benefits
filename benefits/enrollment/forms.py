"""
The enrollment application: Form definitions for results from Hosted Card Verification Flow.
"""
from django import forms


class CardTokenizeSuccessForm(forms.Form):
    """Form to bring client card token back to server."""

    action_url = "enrollment:index"
    id = "card-tokenize-success"
    method = "POST"
    # we don't need recaptcha on this form, it is a single hidden field submitted
    # by a javascript callback
    recaptcha_enabled = False

    # hidden input with no label
    card_token = forms.CharField(widget=forms.HiddenInput(), label="")


class CardTokenizeFailForm(forms.Form):
    """Form to indicate card tokenization failure to server."""

    id = "card-tokenize-fail"
    method = "POST"
    # we don't need recaptcha on this form, it is a single hidden field submitted
    # by a javascript callback
    recaptcha_enabled = False

    def __init__(self, action_url, *args, **kwargs):
        # init super with an empty data dict
        # binds and makes immutable this form's data
        # since there are no form fields, the form is also marked as valid
        super().__init__({}, *args, **kwargs)
        self.action_url = action_url
