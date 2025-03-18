from datetime import timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone

import pytest

from benefits.core.models import EnrollmentFlow, EnrollmentEvent, EnrollmentMethods


@pytest.mark.django_db
def test_EnrollmentFlow_str(model_EnrollmentFlow):
    assert str(model_EnrollmentFlow) == model_EnrollmentFlow.label


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
def test_EnrollmentFlow_enrollment_index_template(model_EnrollmentFlow_with_scope_and_claim):
    assert model_EnrollmentFlow_with_scope_and_claim.enrollment_index_template == "enrollment/index.html"

    model_EnrollmentFlow_with_scope_and_claim.enrollment_index_template_override = "test/enrollment.html"
    model_EnrollmentFlow_with_scope_and_claim.save()

    assert model_EnrollmentFlow_with_scope_and_claim.enrollment_index_template == "test/enrollment.html"


@pytest.mark.django_db
def test_EnrollmentFlow_enrollment_success_template(model_EnrollmentFlow_with_scope_and_claim):
    assert model_EnrollmentFlow_with_scope_and_claim.enrollment_success_template == "enrollment/success.html"


@pytest.mark.django_db
def test_EnrollmentFlow_supported_enrollment_methods(model_EnrollmentFlow_with_scope_and_claim):
    assert model_EnrollmentFlow_with_scope_and_claim.supported_enrollment_methods == ["digital", "in_person"]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "extra_claims,all_claims",
    [
        ("", ["claim"]),
        ("extra_claim", ["claim", "extra_claim"]),
        ("extra_claim_1 extra_claim_2", ["claim", "extra_claim_1", "extra_claim_2"]),
    ],
)
def test_EnrollmentFlow_claims_all_claims(model_EnrollmentFlow_with_scope_and_claim, extra_claims, all_claims):
    model_EnrollmentFlow_with_scope_and_claim.claims_extra_claims = extra_claims
    model_EnrollmentFlow_with_scope_and_claim.save()
    assert model_EnrollmentFlow_with_scope_and_claim.claims_all_claims == all_claims


class SampleFormClass:
    """A class for testing EligibilityVerificationForm references."""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


@pytest.mark.django_db
def test_EnrollmentFlow_eligibility_form_instance(model_EnrollmentFlow_with_eligibility_api):
    model_EnrollmentFlow_with_eligibility_api.eligibility_form_class = f"{__name__}.SampleFormClass"
    model_EnrollmentFlow_with_eligibility_api.save()

    args = (1, "2")
    kwargs = {"one": 1, "two": "2"}
    form_instance = model_EnrollmentFlow_with_eligibility_api.eligibility_form_instance(*args, **kwargs)

    assert isinstance(form_instance, SampleFormClass)
    assert form_instance.args == args
    assert form_instance.kwargs == kwargs


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
        == model_EnrollmentFlow_with_scope_and_claim.claims_provider.client_name
    )


@pytest.mark.django_db
def test_EnrollmentFlow_with_scope_and_claim_no_sign_out(
    model_EnrollmentFlow_with_scope_and_claim, model_ClaimsProvider_no_sign_out
):
    model_EnrollmentFlow_with_scope_and_claim.claims_provider = model_ClaimsProvider_no_sign_out

    assert model_EnrollmentFlow_with_scope_and_claim.uses_claims_verification


@pytest.mark.django_db
def test_EnrollmentFlow_no_scope_and_claim_no_sign_out(model_EnrollmentFlow, model_ClaimsProvider_no_sign_out):
    model_EnrollmentFlow.claims_provider = model_ClaimsProvider_no_sign_out

    assert not model_EnrollmentFlow.uses_claims_verification


@pytest.mark.django_db
def test_EnrollmentFlow_eligibility_api_auth_key(mock_field_secret_value, model_EnrollmentFlow_with_eligibility_api):
    mock_field = mock_field_secret_value(model_EnrollmentFlow_with_eligibility_api, "eligibility_api_auth_key_secret_name")

    assert model_EnrollmentFlow_with_eligibility_api.eligibility_api_auth_key == mock_field.secret_value.return_value
    mock_field.secret_value.assert_called_once_with(model_EnrollmentFlow_with_eligibility_api)


@pytest.mark.django_db
def test_EnrollmentFlow_no_claims_scheme(model_EnrollmentFlow_with_scope_and_claim):
    assert (
        model_EnrollmentFlow_with_scope_and_claim.claims_scheme
        == model_EnrollmentFlow_with_scope_and_claim.claims_provider.scheme
    )


@pytest.mark.django_db
def test_EnrollmentFlow_template_overrides_claims(model_EnrollmentFlow_with_scope_and_claim):
    assert (
        model_EnrollmentFlow_with_scope_and_claim.selection_label_template
        == model_EnrollmentFlow_with_scope_and_claim.selection_label_template_override
    )
    assert model_EnrollmentFlow_with_scope_and_claim.eligibility_unverified_template == "eligibility/unverified.html"
    assert (
        model_EnrollmentFlow_with_scope_and_claim.enrollment_index_template
        == model_EnrollmentFlow_with_scope_and_claim.enrollment_index_template_override
    )
    assert (
        model_EnrollmentFlow_with_scope_and_claim.enrollment_success_template
        == model_EnrollmentFlow_with_scope_and_claim.enrollment_success_template_override
    )

    model_EnrollmentFlow_with_scope_and_claim.selection_label_template_override = ""
    model_EnrollmentFlow_with_scope_and_claim.enrollment_index_template_override = ""
    model_EnrollmentFlow_with_scope_and_claim.enrollment_success_template_override = ""
    model_EnrollmentFlow_with_scope_and_claim.save()

    assert (
        model_EnrollmentFlow_with_scope_and_claim.selection_label_template
        == f"eligibility/includes/selection-label--{model_EnrollmentFlow_with_scope_and_claim.system_name}.html"
    )
    assert model_EnrollmentFlow_with_scope_and_claim.eligibility_unverified_template == "eligibility/unverified.html"
    assert model_EnrollmentFlow_with_scope_and_claim.enrollment_index_template == "enrollment/index.html"
    assert (
        model_EnrollmentFlow_with_scope_and_claim.enrollment_success_template
        == f"enrollment/success--{model_EnrollmentFlow_with_scope_and_claim.transit_agency.slug}.html"
    )


@pytest.mark.django_db
def test_EnrollmentFlow_template_overrides_eligibility_api(model_EnrollmentFlow_with_eligibility_api):
    model_EnrollmentFlow_with_eligibility_api.selection_label_template_override = ""
    model_EnrollmentFlow_with_eligibility_api.enrollment_index_template_override = ""
    model_EnrollmentFlow_with_eligibility_api.enrollment_success_template_override = ""
    model_EnrollmentFlow_with_eligibility_api.save()

    assert (
        model_EnrollmentFlow_with_eligibility_api.selection_label_template
        == f"eligibility/includes/selection-label--{model_EnrollmentFlow_with_eligibility_api.agency_card_name}.html"
    )
    assert (
        model_EnrollmentFlow_with_eligibility_api.eligibility_unverified_template == "eligibility/unverified--agency-card.html"
    )
    assert model_EnrollmentFlow_with_eligibility_api.enrollment_index_template == "enrollment/index--agency-card.html"
    assert (
        model_EnrollmentFlow_with_eligibility_api.enrollment_success_template
        == f"enrollment/success--{model_EnrollmentFlow_with_eligibility_api.agency_card_name}.html"
    )


@pytest.mark.django_db
def test_EnrollmentFlow_clean_supports_expiration(model_EnrollmentFlow_supports_expiration, model_ClaimsProvider):
    # fake a valid claims configuration
    model_EnrollmentFlow_supports_expiration.claims_provider = model_ClaimsProvider
    model_EnrollmentFlow_supports_expiration.claims_scope = "scope"
    model_EnrollmentFlow_supports_expiration.claims_eligibility_claim = "claim"
    # but an invalid reenrollment error template
    model_EnrollmentFlow_supports_expiration.reenrollment_error_template = "does/not/exist.html"

    with pytest.raises(ValidationError, match="Template not found: does/not/exist.html"):
        model_EnrollmentFlow_supports_expiration.clean()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "template_attribute",
    [
        "selection_label_template_override",
        "enrollment_index_template_override",
        "enrollment_success_template_override",
    ],
)
def test_EnrollmentFlow_clean_templates(model_EnrollmentFlow_with_scope_and_claim, model_TransitAgency, template_attribute):
    # remove the agency
    model_EnrollmentFlow_with_scope_and_claim.transit_agency = None
    # set a bad template field
    setattr(model_EnrollmentFlow_with_scope_and_claim, template_attribute, "does/not/exist.html")
    # no agency assigned, OK
    model_EnrollmentFlow_with_scope_and_claim.clean()

    # now assign an agency and expect failure on clean()
    model_EnrollmentFlow_with_scope_and_claim.transit_agency = model_TransitAgency
    with pytest.raises(ValidationError, match="Template not found: does/not/exist.html"):
        model_EnrollmentFlow_with_scope_and_claim.clean()


@pytest.mark.django_db
def test_EnrollmentFlow_clean_in_person_eligibility_context_not_found(model_EnrollmentFlow):
    model_EnrollmentFlow.system_name = "nonexistent_system_name"

    with pytest.raises(
        ValidationError, match=f"{model_EnrollmentFlow.system_name} not configured for In-person. Please uncheck to continue."
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
