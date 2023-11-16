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
    submit_value = _("Choose this Benefit")

    def __init__(self, agency: models.TransitAgency, *args, **kwargs):
        super().__init__(*args, **kwargs)
        verifiers = agency.eligibility_verifiers.filter(active=True)

        self.classes = "col-lg-8"
        # second element is not used since we render the whole label using selection_label_template,
        # therefore set to None
        self.fields["verifier"].choices = [(v.id, None) for v in verifiers]
        self.fields["verifier"].widget.selection_label_templates = {v.id: v.selection_label_template for v in verifiers}

    def clean(self):
        if not recaptcha.verify(self.data):
            raise forms.ValidationError("reCAPTCHA failed")


class EligibilityVerificationForm(forms.Form):
    """Form to collect eligibility verification details."""

    action_url = "eligibility:confirm"
    id = "form-eligibility-verification"
    method = "POST"

    submit_value = _("Check eligibility")
    submitting_value = _("Checking")

    _error_messages = {
        "invalid": _("Check your input. The format looks wrong."),
        "missing": _("This field is required."),
    }

    def __init__(
        self,
        title,
        headline,
        blurb,
        name_label,
        name_placeholder,
        name_help_text,
        sub_label,
        sub_placeholder,
        sub_help_text,
        name_max_length=None,
        sub_input_mode=None,
        sub_max_length=None,
        sub_pattern=None,
        *args,
        **kwargs,
    ):
        """Initialize a new EligibilityVerifier form.

        Args:
            title (str): The page (i.e. tab) title for the form's page.

            headline (str): The <h1> on the form's page.

            blurb (str): Intro <p> on the form's page.

            name_label (str): Label for the name form field.

            name_placeholder (str): Field placeholder for the name form field.

            name_help_text (str): Extra help text for the name form field.

            sub_label (str): Label for the sub form field.

            sub_placeholder (str): Field placeholder for the sub form field.

            sub_help_text (str): Extra help text for the sub form field.

            name_max_length (int): The maximum length accepted for the 'name' API field before sending to this verifier

            sub_input_mode (str): Input mode can be "numeric", "tel", "search", etc. to override default "text" keyboard on
                                  mobile devices

            sub_max_length (int): The maximum length accepted for the 'sub' API field before sending to this verifier

            sub_pattern (str): A regular expression used to validate the 'sub' API field before sending to this verifier

        Extra args and kwargs are passed through to the underlying django.forms.Form.
        """
        super().__init__(auto_id=True, label_suffix="", *args, **kwargs)

        self.title = title
        self.headline = headline
        self.blurb = blurb

        self.classes = "col-lg-6"
        sub_widget = widgets.FormControlTextInput(placeholder=sub_placeholder)
        if sub_pattern:
            sub_widget.attrs.update({"pattern": sub_pattern})
        if sub_input_mode:
            sub_widget.attrs.update({"inputmode": sub_input_mode})
        if sub_max_length:
            sub_widget.attrs.update({"maxlength": sub_max_length})

        self.fields["sub"] = forms.CharField(
            label=sub_label,
            widget=sub_widget,
            help_text=sub_help_text,
        )

        name_widget = widgets.FormControlTextInput(placeholder=name_placeholder)
        if name_max_length:
            name_widget.attrs.update({"maxlength": name_max_length})

        self.fields["name"] = forms.CharField(label=name_label, widget=name_widget, help_text=name_help_text)

    def clean(self):
        if not recaptcha.verify(self.data):
            raise forms.ValidationError("reCAPTCHA failed")


class MSTCourtesyCard(EligibilityVerificationForm):
    """EligibilityVerification form for the MST Courtesy Card."""

    def __init__(self, *args, **kwargs):
        super().__init__(
            title=_("Agency card information"),
            headline=_("Let’s see if we can confirm your eligibility."),
            blurb=_("Please input your Courtesy Card number and last name below to confirm your eligibility."),
            name_label=_("Last name (as it appears on Courtesy Card)"),
            name_placeholder="Garcia",
            name_help_text=_("We use this to help confirm your Courtesy Card."),
            sub_label=_("MST Courtesy Card number"),
            sub_help_text=_("This is a 5-digit number on the front and back of your card."),
            sub_placeholder="12345",
            name_max_length=255,
            sub_input_mode="numeric",
            sub_max_length=5,
            sub_pattern=r"\d{5}",
            *args,
            **kwargs,
        )


class SBMTDMobilityPass(EligibilityVerificationForm):
    """EligibilityVerification form for the SBMTD Mobility Pass."""

    def __init__(self, *args, **kwargs):
        super().__init__(
            title=_("Agency card information"),
            headline=_("Let’s see if we can confirm your eligibility."),
            blurb=_("Please input your Mobility Pass number and last name below to confirm your eligibility."),
            name_label=_("Last name (as it appears on Mobility Pass)"),
            name_placeholder="Garcia",
            name_help_text=_("We use this to help confirm your Mobility Pass."),
            sub_label=_("SBMTD Mobility Pass number"),
            sub_help_text=_("This is a 4-digit number on the back of your card."),
            sub_placeholder="1234",
            name_max_length=255,
            sub_input_mode="numeric",
            sub_max_length=4,
            sub_pattern=r"\d{4}",
            *args,
            **kwargs,
        )
