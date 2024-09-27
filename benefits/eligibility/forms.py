"""
The eligibility application: Form definition for the eligibility verification flow.
"""

import logging

from django import forms
from django.utils.translation import gettext_lazy as _

from benefits.routes import routes
from benefits.core import models, recaptcha, widgets

logger = logging.getLogger(__name__)


class EnrollmentFlowSelectionForm(forms.Form):
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

        self.classes = "col-lg-8"
        # second element is not used since we render the whole label using selection_label_template,
        # therefore set to None
        flow_field = self.fields["flow"]
        flow_field.choices = [(f.id, None) for f in flows]
        flow_field.widget.selection_label_templates = {f.id: f.selection_label_template for f in flows}
        flow_field.widget.attrs.update({"data-custom-validity": _("Please choose a transit benefit.")})
        self.use_custom_validity = True

    def clean(self):
        if not recaptcha.verify(self.data):
            raise forms.ValidationError("reCAPTCHA failed")


class EligibilityVerificationForm(forms.Form):
    """Form to collect eligibility verification details."""

    action_url = routes.ELIGIBILITY_CONFIRM
    id = "form-eligibility-verification"
    method = "POST"

    submit_value = _("Find my record")
    submitting_value = _("Checking")

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
        sub_custom_validity=None,
        name_custom_validity=None,
        *args,
        **kwargs,
    ):
        """Initialize a new EligibilityVerification form.

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

            name_max_length (int): The maximum length accepted for the 'name' API field before sending an API request

            sub_input_mode (str): Input mode can be "numeric", "tel", "search", etc. to override default "text" keyboard on
                                  mobile devices

            sub_max_length (int): The maximum length accepted for the 'sub' API field before sending an API request

            sub_pattern (str): A regular expression used to validate the 'sub' API field before sending an API request

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
        if sub_custom_validity:
            sub_widget.attrs.update({"data-custom-validity": sub_custom_validity})
            self.use_custom_validity = True

        self.fields["sub"] = forms.CharField(
            label=sub_label,
            widget=sub_widget,
            help_text=sub_help_text,
        )

        name_widget = widgets.FormControlTextInput(placeholder=name_placeholder)
        if name_max_length:
            name_widget.attrs.update({"maxlength": name_max_length})
        if name_custom_validity:
            name_widget.attrs.update({"data-custom-validity": name_custom_validity})
            self.use_custom_validity = True

        self.fields["name"] = forms.CharField(label=name_label, widget=name_widget, help_text=name_help_text)

    def clean(self):
        if not recaptcha.verify(self.data):
            raise forms.ValidationError("reCAPTCHA failed")


class CSTAgencyCard(EligibilityVerificationForm):
    """EligibilityVerification form for the CST Agency Card."""

    def __init__(self, *args, **kwargs):
        super().__init__(
            title=_("Agency card information"),
            headline=_("Let’s find the record of your transit benefit."),
            blurb=_(
                "We use the information on your CST Agency Card to find the record of your transit benefit in our system."
            ),
            name_label=_("Last Name"),
            name_placeholder="Hernandez-Demarcos",
            name_help_text=_(
                "Please enter your last name the same way it is printed on your card, including capital letters and hyphens."
            ),
            sub_label=_("Agency Card number"),
            sub_help_text=_("This is a 5-digit number on the front and back of your card."),
            sub_placeholder="12345",
            name_max_length=255,
            sub_input_mode="numeric",
            sub_max_length=5,
            sub_pattern=r"\d{5}",
            sub_custom_validity=_("Please enter a 5-digit number."),
            name_custom_validity=_("Please enter your last name."),
            *args,
            **kwargs,
        )


class MSTCourtesyCard(EligibilityVerificationForm):
    """EligibilityVerification form for the MST Courtesy Card."""

    def __init__(self, *args, **kwargs):
        super().__init__(
            title=_("Agency card information"),
            headline=_("Let’s find the record of your transit benefit."),
            blurb=_(
                "We use the information on your MST Courtesy Card to find the record of your transit benefit in our system."
            ),
            name_label=_("Last Name"),
            name_placeholder="Garcia",
            name_help_text=_(
                "Please enter your last name the same way it is printed on your card, including capital letters and hyphens."
            ),
            sub_label=_("Courtesy Card number"),
            sub_help_text=_("This is a 5-digit number on the front and back of your card."),
            sub_placeholder="12345",
            name_max_length=255,
            sub_input_mode="numeric",
            sub_max_length=5,
            sub_pattern=r"\d{5}",
            sub_custom_validity=_("Please enter a 5-digit number."),
            name_custom_validity=_("Please enter your last name."),
            *args,
            **kwargs,
        )


class SBMTDMobilityPass(EligibilityVerificationForm):
    """EligibilityVerification form for the SBMTD Reduced Fare Mobility ID."""

    def __init__(self, *args, **kwargs):
        super().__init__(
            title=_("Agency card information"),
            headline=_("Let’s find the record of your transit benefit."),
            blurb=_(
                "We use the information on your SBMTD Reduced Fare Mobility ID card to find the record of your transit "
                + "benefit in our system."
            ),
            name_label=_("Last Name"),
            name_placeholder="Garcia",
            name_help_text=_(
                "Please enter your last name the same way it is printed on your card, including capital letters and hyphens."
            ),
            sub_label=_("Reduced Fare Mobility ID card number"),
            sub_help_text=_("This is a 4-digit number on the back of your card."),
            sub_placeholder="1234",
            name_max_length=255,
            sub_input_mode="numeric",
            sub_max_length=4,
            sub_pattern=r"\d{4}",
            sub_custom_validity=_("Please enter a 4-digit number."),
            name_custom_validity=_("Please enter your last name."),
            *args,
            **kwargs,
        )
