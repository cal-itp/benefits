"""
The in-person eligibility application: Form definition for the
in-person eligibility verification flow, in which a
transit agency employee manually verifies a rider's eligibility.
"""

from django import forms
from benefits.routes import routes
from benefits.core import models
from benefits.enrollment.forms import CardTokenizeFailForm, CardTokenizeSuccessForm  # noqa


class InPersonEligibilityForm(forms.Form):
    """Form to capture eligibility for in-person verification flow selection."""

    action_url = routes.IN_PERSON_ELIGIBILITY
    id = "form-flow-selection"
    method = "POST"

    flow = forms.ChoiceField(label="Choose an eligibility type to qualify this rider.", widget=forms.widgets.RadioSelect)

    cancel_url = routes.ADMIN_INDEX

    def __init__(self, agency: models.TransitAgency, *args, **kwargs):
        super().__init__(*args, **kwargs)
        flows = agency.enrollment_flows.filter(supported_enrollment_methods__contains=models.EnrollmentMethods.IN_PERSON)

        self.classes = "in-person-eligibility-form"
        flow_field = self.fields["flow"]
        flow_field.choices = [(f.id, f.label) for f in flows]
        flow_field.widget.attrs.update({"data-custom-validity": "Please choose an eligibility type."})

        # dynamically add a BooleanField for each flow
        for flow in flows:
            field_id = f"verified_{flow.id}"
            self.fields[field_id] = forms.BooleanField(
                label=self.get_policy_details(flow), widget=forms.widgets.CheckboxInput(attrs={"class": "d-none"})
            )
            field = self.fields[field_id]
            field.hide = True
            field.widget.attrs.update(
                {"data-custom-validity": "Please confirm you have used an agency policy to verify eligibility."}
            )

        self.use_custom_validity = True

    def get_policy_details(self, flow: models.EnrollmentFlow):
        eligibility_context = flow.in_person_eligibility_context

        return eligibility_context["policy_details"] if eligibility_context else None
