"""
The eligibility application: Form definition for the eligibility verification flow.
"""

import logging

from django import forms
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

from benefits.core import models, widgets
from benefits.core.mixins import ValidateRecaptchaMixin
from benefits.routes import routes

logger = logging.getLogger(__name__)


class EnrollmentFlowSelectionForm(ValidateRecaptchaMixin, forms.Form):
    """Form to capture enrollment flow selection."""

    action_url = routes.ELIGIBILITY_INDEX
    id = "form-flow-selection"
    method = "POST"

    flow = forms.ChoiceField(label="", widget=widgets.FlowRadioSelect)
    # sets label to empty string so the radio_select template can override the label style
    submit_value = _("Choose this benefit")

    def __init__(self, agency: models.TransitAgency, *args, **kwargs):
        super().__init__(*args, **kwargs)
        flows = agency.enrollment_flows.filter(supported_enrollment_methods__contains=models.EnrollmentMethods.DIGITAL)

        # second element is not used since we render the whole label using selection_label_template,
        # therefore set to None
        flow_field = self.fields["flow"]
        flow_field.choices = [(f.id, None) for f in flows]
        flow_field.widget.selection_label_templates = {f.id: f.selection_label_template for f in flows}
        flow_field.widget.attrs.update({"data-custom-validity": _("Please choose a transit benefit.")})
        self.use_custom_validity = True


class EligibilityVerificationForm(ValidateRecaptchaMixin, forms.Form):
    """Base form to collect eligibility verification details."""

    action_url = routes.ELIGIBILITY_CONFIRM
    id = "form-eligibility-verification"
    method = "POST"

    submit_value = _("Find my record")
    submitting_value = _("Checking")
    classes = "eligibility-verification-form"

    # Default configuration attributes (override in subclasses)
    title = _("Agency card information")
    headline = _("Let’s find the record of your transit benefit.")
    blurb = None

    name_label = _("Last Name")
    name_placeholder = "Garcia"
    name_help_text = _(
        "Please enter your last name the same way it is printed on your card, including capital letters and hyphens."
    )
    name_max_length = 255
    name_custom_validity = _("Please enter your last name.")

    sub_label = None
    sub_placeholder = None
    sub_help_text = None
    sub_input_mode = None
    sub_max_length = None
    sub_pattern = None
    sub_custom_validity = None

    def __init__(self, *args, **kwargs):
        """Initialize the form using class attributes for configuration."""
        super().__init__(auto_id=True, label_suffix="", *args, **kwargs)

        # Configure the 'sub' field (ID/Card Number)
        sub_widget = widgets.FormControlTextInput(placeholder=self.sub_placeholder)

        if self.sub_pattern:
            sub_widget.attrs.update({"pattern": self.sub_pattern})
        if self.sub_input_mode:
            sub_widget.attrs.update({"inputmode": self.sub_input_mode})
        if self.sub_max_length:
            sub_widget.attrs.update({"maxlength": self.sub_max_length})
        if self.sub_custom_validity:
            sub_widget.attrs.update({"data-custom-validity": self.sub_custom_validity})
            self.use_custom_validity = True

        sub_validators = []
        if self.sub_pattern and self.sub_custom_validity:
            sub_validators.append(RegexValidator(regex=self.sub_pattern, message=self.sub_custom_validity))

        self.fields["sub"] = forms.CharField(
            label=self.sub_label,
            widget=sub_widget,
            help_text=self.sub_help_text,
            max_length=self.sub_max_length,
            validators=sub_validators,
        )

        # Configure the 'name' field
        name_widget = widgets.FormControlTextInput(placeholder=self.name_placeholder)

        if self.name_max_length:
            name_widget.attrs.update({"maxlength": self.name_max_length})
        if self.name_custom_validity:
            name_widget.attrs.update({"data-custom-validity": self.name_custom_validity})
            self.use_custom_validity = True

        self.fields["name"] = forms.CharField(
            label=self.name_label,
            widget=name_widget,
            help_text=self.name_help_text,
            max_length=self.name_max_length,
        )


class MSTCourtesyCard(EligibilityVerificationForm):
    """EligibilityVerification form for the MST Courtesy Card."""

    blurb = _("We use the information on your MST Courtesy Card to find the record of your transit benefit in our system.")

    sub_label = _("Courtesy Card number")
    sub_placeholder = "12345"
    sub_help_text = _("This is a 5-digit number on the front and back of your card.")
    sub_input_mode = "numeric"
    sub_max_length = 5
    sub_pattern = r"\d{5}"
    sub_custom_validity = _("Please enter a 5-digit number.")


class CSTAgencyCard(MSTCourtesyCard):
    """
    EligibilityVerification form for the CST Agency Card.
    Inherits validation logic from MSTCourtesyCard but overrides specific text.
    """

    blurb = _("We use the information on your CST Agency Card to find the record of your transit benefit in our system.")

    sub_label = _("Agency Card number")


class SBMTDMobilityPass(EligibilityVerificationForm):
    """EligibilityVerification form for the SBMTD Reduced Fare Mobility ID."""

    blurb = _(
        "We use the information on your SBMTD Reduced Fare Mobility ID card to find the record of your transit benefit in our system."  # noqa: E501
    )

    sub_label = _("Reduced Fare Mobility ID card number")
    sub_placeholder = "12345"
    sub_help_text = _("This is a 4- or 5-digit number on the back of your card.")
    sub_input_mode = "numeric"
    sub_max_length = 5
    sub_pattern = r"\d{4,5}"
    sub_custom_validity = _("Please enter a 4- or 5-digit number.")
