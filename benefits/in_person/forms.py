"""
The in-person eligibility application: Form definition for the
in-person eligibility verification flow, in which a
transit agency employee manually verifies a rider's eligibility.
"""

from django import forms
from benefits.routes import routes
from benefits.core import models


class InPersonEligibilityForm(forms.Form):
    """Form to capture eligibility for in-person verification flow selection."""

    action_url = routes.IN_PERSON_ELIGIBILITY
    id = "form-flow-selection"
    method = "POST"

    flow = forms.ChoiceField(label="Choose an eligibility type to qualify this rider.", widget=forms.widgets.RadioSelect)
    verified = forms.BooleanField(label="I have verified this person’s eligibility for a transit benefit.", required=True)

    cancel_url = routes.ADMIN_INDEX

    def __init__(self, agency: models.TransitAgency, *args, **kwargs):
        super().__init__(*args, **kwargs)
        flows = agency.enrollment_flows.all()

        self.classes = "checkbox-parent"
        flow_field = self.fields["flow"]
        flow_field.choices = [(f.id, f.label) for f in flows]
        flow_field.widget.attrs.update({"data-custom-validity": "Please choose a transit benefit."})
        self.use_custom_validity = True
