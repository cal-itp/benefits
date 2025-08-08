import pytest

from benefits.core import models
from benefits.in_person.forms import InPersonEligibilityForm


@pytest.mark.django_db
def test_eligibility_logged_in_filtering_flows(model_TransitAgency):
    digital = models.EnrollmentFlow.objects.create(
        transit_agency=model_TransitAgency, supported_enrollment_methods=[models.EnrollmentMethods.DIGITAL], label="Digital"
    )
    in_person = models.EnrollmentFlow.objects.create(
        transit_agency=model_TransitAgency,
        supported_enrollment_methods=[models.EnrollmentMethods.IN_PERSON],
        label="In-Person",
    )
    both = models.EnrollmentFlow.objects.create(
        transit_agency=model_TransitAgency,
        supported_enrollment_methods=[models.EnrollmentMethods.DIGITAL, models.EnrollmentMethods.IN_PERSON],
        label="Both",
    )
    form = InPersonEligibilityForm(agency=model_TransitAgency)

    filtered_flow_ids = [choice[0] for choice in form.fields["flow"].choices]

    assert in_person.id, both.id in filtered_flow_ids
    assert digital.id not in filtered_flow_ids
