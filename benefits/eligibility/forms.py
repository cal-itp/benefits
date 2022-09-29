"""
The eligibility application: Form definition for the eligibility verification flow.
"""
import logging

from django import forms
from django.utils.translation import gettext_lazy as _

from benefits.core import models, recaptcha, widgets


logger = logging.getLogger(__name__)


class EligibilityVerifierSelectionForm(forms.Form):
    """Form to capture eligibility verifier selection."""

    action_url = "eligibility:index"
    method = "POST"

    verifier = forms.ChoiceField(label=_("eligibility.pages.index.label"), widget=widgets.RadioSelect)

    submit_value = _("eligibility.buttons.choose")

    def __init__(self, agency: models.TransitAgency, *args, **kwargs):
        super().__init__(*args, **kwargs)
        verifiers = agency.eligibility_verifiers.all()

        self.fields["verifier"].choices = [(v.id, _(v.selection_label)) for v in verifiers]
        self.fields["verifier"].widget.choice_descriptions = {
            v.id: _(v.selection_label_description) for v in verifiers if v.selection_label_description
        }


class EligibilityVerificationForm(forms.Form):
    """Form to collect eligibility verification details."""

    action_url = "eligibility:confirm"
    method = "POST"

    submit_value = _("eligibility.forms.confirm.submit")
    submitting_value = _("eligibility.forms.confirm.submitting")

    _error_messages = {
        "invalid": _("eligibility.forms.confirm.errors.invalid"),
        "missing": _("eligibility.forms.confirm.errors.missing"),
    }

    def __init__(self, verifier: models.EligibilityVerifier, *args, **kwargs):
        super().__init__(*args, **kwargs)

        sub_widget = widgets.FormControlTextInput(placeholder=verifier.form_sub_placeholder)
        if verifier.form_sub_pattern:
            sub_widget.attrs.update({"pattern": verifier.form_sub_pattern})

        self.fields["sub"] = forms.CharField(
            label=_(verifier.form_sub_label),
            widget=sub_widget,
            help_text=_(verifier.form_sub_help_text),
        )

        name_widget = widgets.FormControlTextInput(placeholder=verifier.form_name_placeholder)
        if verifier.form_name_max_length:
            name_widget.attrs.update({"maxlength": verifier.form_name_max_length})

        self.fields["name"] = forms.CharField(
            label=_(verifier.form_name_label), widget=name_widget, help_text=_(verifier.form_name_help_text)
        )

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
