from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from benefits.core.models import EligibilityApiVerificationRequest, EnrollmentEvent, EnrollmentFlow, EnrollmentMethods


@pytest.mark.django_db
class TestEligibilityApiVerificationRequest:
    @pytest.fixture(autouse=True)
    def init(self, model_EligibilityApiVerificationRequest: EligibilityApiVerificationRequest):
        self.model = model_EligibilityApiVerificationRequest

    def test_api_auth_key(self, mock_field_secret_value):
        mock_field = mock_field_secret_value(self.model, "api_auth_key_secret_name")

        assert self.model.api_auth_key == mock_field.secret_value.return_value
        mock_field.secret_value.assert_called_once_with(self.model)

    def test_api_public_key_data(self, model_PemData):
        assert self.model.api_public_key_data == model_PemData.data

    def test_str(self):
        assert str(self.model) == self.model.label


@pytest.mark.django_db
def test_EnrollmentFlow_str(model_EnrollmentFlow):
    assert str(model_EnrollmentFlow) == f"{model_EnrollmentFlow.label} ({model_EnrollmentFlow.transit_agency.slug})"


@pytest.mark.django_db
def test_EnrollmentFlow_str_no_agency(model_EnrollmentFlow):
    model_EnrollmentFlow.transit_agency = None
    assert str(model_EnrollmentFlow) == f"{model_EnrollmentFlow.label} (no agency)"


@pytest.mark.django_db
def test_EnrollmentFlow_agency_card_name(model_EnrollmentFlow_with_eligibility_api):
    assert (
        model_EnrollmentFlow_with_eligibility_api.agency_card_name
        == f"{model_EnrollmentFlow_with_eligibility_api.transit_agency.slug}-agency-card"
    )


@pytest.mark.django_db
def test_EnrollmentFlow_agency_card_name__claims(model_EnrollmentFlow_with_scope_and_claim):
    assert model_EnrollmentFlow_with_scope_and_claim.agency_card_name == ""


@pytest.mark.django_db
def test_EnrollmentFlow_supported_enrollment_methods(model_EnrollmentFlow_with_scope_and_claim):
    assert model_EnrollmentFlow_with_scope_and_claim.supported_enrollment_methods == ["digital", "in_person"]


@pytest.mark.django_db
def test_EnrollmentFlow_by_id_matching(model_EnrollmentFlow):
    flow = EnrollmentFlow.by_id(model_EnrollmentFlow.id)

    assert flow == model_EnrollmentFlow


@pytest.mark.django_db
def test_EnrollmentFlow_by_id_nonmatching():
    with pytest.raises(EnrollmentFlow.DoesNotExist):
        EnrollmentFlow.by_id(99999)


@pytest.mark.django_db
def test_EnrollmentFlow_with_scope_and_claim(model_EnrollmentFlow_with_scope_and_claim):

    assert model_EnrollmentFlow_with_scope_and_claim.uses_claims_verification
    assert (
        model_EnrollmentFlow_with_scope_and_claim.eligibility_verifier
        == model_EnrollmentFlow_with_scope_and_claim.oauth_config.client_name
    )


@pytest.mark.django_db
def test_EnrollmentFlow_with_scope_and_claim_no_sign_out(model_EnrollmentFlow_with_scope_and_claim):
    model_EnrollmentFlow_with_scope_and_claim.sign_out_button_template = ""
    model_EnrollmentFlow_with_scope_and_claim.sign_out_link_template = ""

    assert model_EnrollmentFlow_with_scope_and_claim.uses_claims_verification


@pytest.mark.django_db
def test_EnrollmentFlow_no_scope_and_claim_no_sign_out(model_EnrollmentFlow):
    model_EnrollmentFlow.sign_out_button_template = ""
    model_EnrollmentFlow.sign_out_link_template = ""

    assert not model_EnrollmentFlow.uses_claims_verification


@pytest.mark.django_db
def test_EnrollmentFlow_eligibility_api_auth_key(model_EnrollmentFlow_with_eligibility_api):
    assert (
        model_EnrollmentFlow_with_eligibility_api.eligibility_api_auth_key
        == model_EnrollmentFlow_with_eligibility_api.api_request.api_auth_key
    )


@pytest.mark.django_db
def test_EnrollmentFlow_eligibility_api_public_key_data(model_EnrollmentFlow_with_eligibility_api):
    assert (
        model_EnrollmentFlow_with_eligibility_api.eligibility_api_public_key_data
        == model_EnrollmentFlow_with_eligibility_api.api_request.api_public_key_data
    )


@pytest.mark.django_db
def test_EnrollmentFlow_no_claims_scheme(model_EnrollmentFlow_with_scope_and_claim):
    assert (
        model_EnrollmentFlow_with_scope_and_claim.claims_scheme
        == model_EnrollmentFlow_with_scope_and_claim.oauth_config.scheme
    )


@pytest.mark.django_db
def test_EnrollmentFlow_template_claims(model_EnrollmentFlow_with_scope_and_claim):
    assert (
        model_EnrollmentFlow_with_scope_and_claim.selection_label_template
        == f"eligibility/includes/selection-label--{model_EnrollmentFlow_with_scope_and_claim.system_name}.html"
    )


@pytest.mark.django_db
def test_EnrollmentFlow_template_eligibility_api(model_EnrollmentFlow_with_eligibility_api):
    assert (
        model_EnrollmentFlow_with_eligibility_api.selection_label_template
        == f"eligibility/includes/selection-label--{model_EnrollmentFlow_with_eligibility_api.agency_card_name}.html"
    )


@pytest.mark.django_db
def test_EnrollmentFlow_clean_in_person_eligibility_context_not_found(model_EnrollmentFlow):
    model_EnrollmentFlow.system_name = "nonexistent_system_name"

    with pytest.raises(
        ValidationError, match=f"{model_EnrollmentFlow.system_name} not configured for In-person. Please uncheck to continue."
    ):
        model_EnrollmentFlow.clean()


@pytest.mark.django_db
def test_EnrollmentFlow_clean_group_id(model_EnrollmentFlow):
    assert not hasattr(model_EnrollmentFlow, "enrollmentgroup")

    with pytest.raises(
        ValidationError,
        match=f"{model_EnrollmentFlow.system_name} needs either a LittlepayGroup or SwitchioGroup linked to it.",
    ):
        model_EnrollmentFlow.clean()


@pytest.mark.django_db
def test_EnrollmentEvent_create(model_TransitAgency, model_EnrollmentFlow):
    ts = timezone.now()
    event = EnrollmentEvent.objects.create(
        transit_agency=model_TransitAgency,
        enrollment_flow=model_EnrollmentFlow,
        enrollment_method=EnrollmentMethods.DIGITAL,
        verified_by="Test",
    )

    assert event.transit_agency == model_TransitAgency
    assert event.enrollment_flow == model_EnrollmentFlow
    assert event.enrollment_method == EnrollmentMethods.DIGITAL
    assert event.verified_by == "Test"
    # default enrollment_datetime should be nearly the same as the timestamp
    assert event.enrollment_datetime - ts <= timedelta(milliseconds=1)

    dt = timezone.datetime(2024, 9, 13, 13, 30, 0, tzinfo=timezone.get_default_timezone())
    expiry = dt + timedelta(weeks=52)
    event = EnrollmentEvent(
        transit_agency=model_TransitAgency,
        enrollment_flow=model_EnrollmentFlow,
        enrollment_method=EnrollmentMethods.DIGITAL,
        verified_by="Test",
        enrollment_datetime=dt,
        expiration_datetime=expiry,
    )
    # enrollment_datetime should equal the given value exactly
    assert event.enrollment_datetime == dt
    assert event.expiration_datetime == expiry


@pytest.mark.django_db
def test_EnrollmentEvent_str(model_TransitAgency, model_EnrollmentFlow):
    ts = timezone.datetime(2024, 9, 13, 13, 30, 0, tzinfo=timezone.get_default_timezone())

    event = EnrollmentEvent.objects.create(
        transit_agency=model_TransitAgency,
        enrollment_flow=model_EnrollmentFlow,
        enrollment_method=EnrollmentMethods.DIGITAL,
        verified_by="Test",
        enrollment_datetime=ts,
    )
    event_str = str(event)

    assert "Sep 13, 2024, 01:30 PM" in event_str
    assert str(event.transit_agency) in event_str
    assert str(event.enrollment_flow) in event_str
