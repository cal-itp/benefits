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
    id = "form-verifier-selection"
    method = "POST"

    verifier = forms.ChoiceField(label="", widget=widgets.VerifierRadioSelect)
    # sets label to empty string so the radio_select template can override the label style
    submit_value = _("eligibility.buttons.choose")

    def __init__(self, agency: models.TransitAgency, csp_nonce=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        verifiers = agency.eligibility_verifiers.all()

        self.classes = "offset-lg-1 col-lg-9"
        # second element is not used since we render the whole label using selection_label_template,
        # therefore set to None
        self.fields["verifier"].choices = [(v.id, None) for v in verifiers]
        self.fields["verifier"].widget.selection_label_templates = {v.id: v.selection_label_template for v in verifiers}
        self.fields["verifier"].widget.csp_nonce = csp_nonce

    def clean(self):
        if not recaptcha.verify(self.data):
            raise forms.ValidationError("reCAPTCHA failed")


class EligibilityVerificationForm(forms.Form):
    """Form to collect eligibility verification details."""

    action_url = "eligibility:confirm"
    id = "form-eligibility-verification"
    method = "POST"

    submit_value = _("eligibility.forms.confirm.submit")
    submitting_value = _("eligibility.forms.confirm.submitting")

    _error_messages = {
        "invalid": _("eligibility.forms.confirm.errors.invalid"),
        "missing": _("eligibility.forms.confirm.errors.missing"),
    }

    def __init__(self, verifier: models.EligibilityVerifier, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.classes = "offset-lg-3 col-lg-6"
        sub_widget = widgets.FormControlTextInput(placeholder=verifier.form_sub_placeholder)
        if verifier.form_sub_pattern:
            sub_widget.attrs.update({"pattern": verifier.form_sub_pattern})
        if verifier.form_input_mode:
            sub_widget.attrs.update({"inputmode": verifier.form_input_mode})
        if verifier.form_max_length:
            sub_widget.attrs.update({"maxlength": verifier.form_max_length})

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

    def clean(self):
        if not recaptcha.verify(self.data):
            raise forms.ValidationError("reCAPTCHA failed")
