"""
The eligibility application: Form definition for the eligibility verification flow.
"""
from django import forms
from django.utils.translation import ugettext_lazy as _

from benefits.core import widgets


class EligibilityVerificationForm(forms.Form):
    """Form to collect eligibility verification details."""

    action_url = "eligibility:confirm"
    method = "POST"

    sub = forms.CharField(
        label=_("CA driver’s license or ID number"),
        widget=widgets.FormControlTextInput(placeholder="A1234567")
    )

    name = forms.CharField(
        label=_("Last name (as it appears on ID)"),
        widget=widgets.FormControlTextInput(placeholder="Rodriguez")
    )

    submit_value = _("Check status")
    submitting_value = _("Checking")

    _error_messages = {
        "invalid": _("Check your input. The format looks wrong."),
        "missing": _("This field is required.")
    }

    def add_api_errors(self, form_errors):
        """Handle errors passed back from API server related to submitted form values."""

        for form_error in form_errors:
            field_errors = [
                (field, code)
                for field, code in form_error.items()
                if field in self.fields
            ]

            validation_errors = {
                field: forms.ValidationError(self._error_messages.get(code, _("Error")), code=code)
                for (field, code) in field_errors
            }

            for (field, err) in validation_errors.items():
                self.add_error(field, err)
