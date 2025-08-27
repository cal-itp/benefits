import pytest

from benefits.core import models
from benefits.eligibility.forms import CSTAgencyCard, MSTCourtesyCard, SBMTDMobilityPass, EnrollmentFlowSelectionForm


@pytest.mark.django_db
def test_EnrollmentFlowSelectionForm_filtering_flows(model_TransitAgency):
    digital = models.EnrollmentFlow.objects.create(
        transit_agency=model_TransitAgency,
        supported_enrollment_methods=[models.EnrollmentMethods.DIGITAL],
        label="Digital",
        selection_label_template_override="eligibility/includes/selection-label.html",
    )
    in_person = models.EnrollmentFlow.objects.create(
        transit_agency=model_TransitAgency,
        supported_enrollment_methods=[models.EnrollmentMethods.IN_PERSON],
        label="In-Person",
        selection_label_template_override="eligibility/includes/selection-label.html",
    )
    both = models.EnrollmentFlow.objects.create(
        transit_agency=model_TransitAgency,
        supported_enrollment_methods=[models.EnrollmentMethods.DIGITAL, models.EnrollmentMethods.IN_PERSON],
        label="Both",
        selection_label_template_override="eligibility/includes/selection-label.html",
    )

    form = EnrollmentFlowSelectionForm(agency=model_TransitAgency)

    filtered_flow_ids = [choice[0] for choice in form.fields["flow"].choices]

    assert digital.id, both.id in filtered_flow_ids
    assert in_person.id not in filtered_flow_ids


def test_CSTAgencyCard():
    form = CSTAgencyCard(data={"sub": "12345", "name": "Gonzalez"})

    assert form.is_valid()

    sub_attrs = form.fields["sub"].widget.attrs
    assert sub_attrs["pattern"] == r"\d{5}"
    assert sub_attrs["inputmode"] == "numeric"
    assert sub_attrs["maxlength"] == 5
    assert sub_attrs["data-custom-validity"] == "Please enter a 5-digit number."

    name_attrs = form.fields["name"].widget.attrs
    assert name_attrs["maxlength"] == 255
    assert name_attrs["data-custom-validity"] == "Please enter your last name."

    assert form.use_custom_validity


def test_MSTCourtesyCard():
    form = MSTCourtesyCard(data={"sub": "12345", "name": "Gonzalez"})

    assert form.is_valid()

    sub_attrs = form.fields["sub"].widget.attrs
    assert sub_attrs["pattern"] == r"\d{5}"
    assert sub_attrs["inputmode"] == "numeric"
    assert sub_attrs["maxlength"] == 5
    assert sub_attrs["data-custom-validity"] == "Please enter a 5-digit number."

    name_attrs = form.fields["name"].widget.attrs
    assert name_attrs["maxlength"] == 255
    assert name_attrs["data-custom-validity"] == "Please enter your last name."

    assert form.use_custom_validity


def test_SBMTDMobilityPass():
    form = SBMTDMobilityPass(data={"sub": "1234", "name": "Barbara"})

    assert form.is_valid()

    sub_attrs = form.fields["sub"].widget.attrs
    assert sub_attrs["pattern"] == r"\d{4,5}"
    assert sub_attrs["maxlength"] == 5
    assert sub_attrs["inputmode"] == "numeric"
    assert sub_attrs["data-custom-validity"] == "Please enter a 4- or 5-digit number."

    name_attrs = form.fields["name"].widget.attrs
    assert name_attrs["maxlength"] == 255
    assert name_attrs["data-custom-validity"] == "Please enter your last name."

    assert form.use_custom_validity
