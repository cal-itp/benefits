"""
The eligibility application: Form definition for the eligibility verification flow.
"""
import logging

from django import forms
from django.utils.translation import gettext_lazy as _

from benefits.core import recaptcha, widgets


logger = logging.getLogger(__name__)


class EligibilityVerificationForm(forms.Form):
    """Form to collect eligibility verification details."""

    action_url = "eligibility:confirm"
    method = "POST"

    sub = forms.CharField(
        label=_("eligibility.forms.confirm.fields.sub"), widget=widgets.FormControlTextInput(placeholder="A1234567")
    )

    name = forms.CharField(
        label=_("eligibility.forms.confirm.fields.name"), widget=widgets.FormControlTextInput(placeholder="Rodriguez")
    )

    submit_value = _("eligibility.forms.confirm.submit")
    submitting_value = _("eligibility.forms.confirm.submitting")

    _error_messages = {
        "invalid": _("eligibility.forms.confirm.errors.invalid"),
        "missing": _("eligibility.forms.confirm.errors.missing"),
    }

    def add_api_errors(self, form_errors):
        """Handle errors passed back from API server related to submitted form values."""

        validation_errors = {
            field: forms.ValidationError(self._error_messages.get(code, _("core.pages.error.title")), code=code)
            for (field, code) in form_errors.items()
            if field in self.fields
        }

        if len(validation_errors) > 0:
            logger.warning("Form fields are invalid")

        for (field, err) in validation_errors.items():
            self.add_error(field, err)

    def clean(self):
        if not recaptcha.verify(self.data):
            raise forms.ValidationError("reCAPTCHA failed")
