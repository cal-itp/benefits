from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.utils import timezone

import pytest

from benefits.core.models import (
    template_path,
    SecretNameField,
    EnrollmentFlow,
    TransitAgency,
    EnrollmentEvent,
    EnrollmentMethods,
    agency_logo_small,
    agency_logo_large,
)
import benefits.secrets


@pytest.fixture
def mock_requests_get_pem_data(mocker):
    # intercept and spy on the GET request
    return mocker.patch("benefits.core.models.requests.get", return_value=mocker.Mock(text="PEM text"))


@pytest.mark.django_db
@pytest.mark.parametrize(
    "input_template,expected_path",
    [
        ("error-base.html", f"{settings.BASE_DIR}/benefits/templates/error-base.html"),
        ("core/index.html", f"{settings.BASE_DIR}/benefits/core/templates/core/index.html"),
        ("eligibility/start.html", f"{settings.BASE_DIR}/benefits/eligibility/templates/eligibility/start.html"),
        ("", None),
        ("nope.html", None),
        ("core/not-there.html", None),
    ],
)
def test_template_path(input_template, expected_path):
    if expected_path:
        assert template_path(input_template) == Path(expected_path)
    else:
        assert template_path(input_template) is None


def test_SecretNameField_init():
    field = SecretNameField()

    assert benefits.secrets.NAME_VALIDATOR in field.validators
    assert field.max_length == 127
    assert field.blank is False
    assert field.null is False
    assert field.allow_unicode is False
    assert field.description is not None
    assert field.description != ""


def test_SecretNameField_init_null_blank():
    field = SecretNameField(blank=True, null=True)

    assert field.blank is True
    assert field.null is True


@pytest.mark.django_db
def test_PemData_str(model_PemData):
    assert str(model_PemData) == model_PemData.label


@pytest.mark.django_db
def test_PemData_data_text_secret_name(model_PemData, mock_models_get_secret_by_name):
    # a secret name and not remote URL, should use secret value

    data = model_PemData.data

    mock_models_get_secret_by_name.assert_called_once_with(model_PemData.text_secret_name)
    assert data == mock_models_get_secret_by_name.return_value


@pytest.mark.django_db
def test_PemData_data_remote(model_PemData, mock_requests_get_pem_data):
    # a remote URL and no secret name, should use remote value

    model_PemData.text_secret_name = None
    model_PemData.remote_url = "http://localhost/publickey"

    assert not model_PemData.text_secret_name

    data = model_PemData.data

    mock_requests_get_pem_data.assert_called_once_with(model_PemData.remote_url, timeout=settings.REQUESTS_TIMEOUT)
    assert data == mock_requests_get_pem_data.return_value.text


@pytest.mark.django_db
def test_PemData_data_text_secret_name_and_remote__uses_text_secret(
    model_PemData, mock_models_get_secret_by_name, mock_requests_get_pem_data
):
    # a remote URL and the secret value is not None, should use the secret value

    model_PemData.remote_url = "http://localhost/publickey"

    data = model_PemData.data

    mock_models_get_secret_by_name.assert_called_once_with(model_PemData.text_secret_name)
    mock_requests_get_pem_data.assert_called_once_with(model_PemData.remote_url, timeout=settings.REQUESTS_TIMEOUT)
    assert data == mock_models_get_secret_by_name.return_value


@pytest.mark.django_db
def test_PemData_data_text_secret_name_and_remote__uses_remote(
    model_PemData, mock_models_get_secret_by_name, mock_requests_get_pem_data
):
    # a remote URL and the secret value is None, should use remote value
    model_PemData.remote_url = "http://localhost/publickey"
    mock_models_get_secret_by_name.return_value = None

    data = model_PemData.data

    mock_models_get_secret_by_name.assert_called_once_with(model_PemData.text_secret_name)
    mock_requests_get_pem_data.assert_called_once_with(model_PemData.remote_url, timeout=settings.REQUESTS_TIMEOUT)
    assert data == mock_requests_get_pem_data.return_value.text


@pytest.mark.django_db
def test_model_ClaimsProvider(model_ClaimsProvider):
    assert model_ClaimsProvider.supports_sign_out
    assert str(model_ClaimsProvider) == model_ClaimsProvider.client_name


@pytest.mark.django_db
def test_model_ClaimsProvider_client_id(model_ClaimsProvider, mock_models_get_secret_by_name):
    secret_value = model_ClaimsProvider.client_id

    mock_models_get_secret_by_name.assert_called_once_with(model_ClaimsProvider.client_id_secret_name)
    assert secret_value == mock_models_get_secret_by_name.return_value


@pytest.mark.django_db
def test_model_ClaimsProvider_no_sign_out(model_ClaimsProvider_no_sign_out):
    assert not model_ClaimsProvider_no_sign_out.supports_sign_out


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
def test_EnrollmentFlow_eligibility_start_template(model_EnrollmentFlow):
    assert model_EnrollmentFlow.eligibility_start_template == "eligibility/start.html"


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
def test_EnrollmentFlow_eligibility_api_auth_key(model_EnrollmentFlow_with_eligibility_api, mock_models_get_secret_by_name):
    secret_value = model_EnrollmentFlow_with_eligibility_api.eligibility_api_auth_key

    mock_models_get_secret_by_name.assert_called_once_with(
        model_EnrollmentFlow_with_eligibility_api.eligibility_api_auth_key_secret_name
    )
    assert secret_value == mock_models_get_secret_by_name.return_value


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
    assert (
        model_EnrollmentFlow_with_scope_and_claim.eligibility_start_template
        == model_EnrollmentFlow_with_scope_and_claim.eligibility_start_template_override
    )
    assert (
        model_EnrollmentFlow_with_scope_and_claim.eligibility_unverified_template
        == model_EnrollmentFlow_with_scope_and_claim.eligibility_unverified_template_override
    )
    assert (
        model_EnrollmentFlow_with_scope_and_claim.enrollment_index_template
        == model_EnrollmentFlow_with_scope_and_claim.enrollment_index_template_override
    )
    assert (
        model_EnrollmentFlow_with_scope_and_claim.enrollment_success_template
        == model_EnrollmentFlow_with_scope_and_claim.enrollment_success_template_override
    )

    model_EnrollmentFlow_with_scope_and_claim.selection_label_template_override = ""
    model_EnrollmentFlow_with_scope_and_claim.eligibility_start_template_override = ""
    model_EnrollmentFlow_with_scope_and_claim.eligibility_unverified_template_override = ""
    model_EnrollmentFlow_with_scope_and_claim.enrollment_index_template_override = ""
    model_EnrollmentFlow_with_scope_and_claim.enrollment_success_template_override = ""
    model_EnrollmentFlow_with_scope_and_claim.save()

    assert (
        model_EnrollmentFlow_with_scope_and_claim.selection_label_template
        == f"eligibility/includes/selection-label--{model_EnrollmentFlow_with_scope_and_claim.system_name}.html"
    )
    assert (
        model_EnrollmentFlow_with_scope_and_claim.eligibility_start_template
        == f"eligibility/start--{model_EnrollmentFlow_with_scope_and_claim.system_name}.html"
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
    model_EnrollmentFlow_with_eligibility_api.eligibility_start_template_override = ""
    model_EnrollmentFlow_with_eligibility_api.eligibility_unverified_template_override = ""
    model_EnrollmentFlow_with_eligibility_api.enrollment_index_template_override = ""
    model_EnrollmentFlow_with_eligibility_api.enrollment_success_template_override = ""
    model_EnrollmentFlow_with_eligibility_api.save()

    assert (
        model_EnrollmentFlow_with_eligibility_api.selection_label_template
        == f"eligibility/includes/selection-label--{model_EnrollmentFlow_with_eligibility_api.agency_card_name}.html"
    )
    assert (
        model_EnrollmentFlow_with_eligibility_api.eligibility_start_template
        == f"eligibility/start--{model_EnrollmentFlow_with_eligibility_api.agency_card_name}.html"
    )
    assert (
        model_EnrollmentFlow_with_eligibility_api.eligibility_unverified_template
        == f"eligibility/unverified--{model_EnrollmentFlow_with_eligibility_api.agency_card_name}.html"
    )
    assert model_EnrollmentFlow_with_eligibility_api.enrollment_index_template == "enrollment/index--agency-card.html"
    assert (
        model_EnrollmentFlow_with_eligibility_api.enrollment_success_template
        == f"enrollment/success--{model_EnrollmentFlow_with_eligibility_api.agency_card_name}.html"
    )


@pytest.mark.django_db
def test_EnrollmentFlow_clean_claims_verification(model_EnrollmentFlow_with_scope_and_claim, model_TransitAgency):
    # remove agency
    model_EnrollmentFlow_with_scope_and_claim.transit_agency = None
    # and required fields
    model_EnrollmentFlow_with_scope_and_claim.claims_scope = ""
    model_EnrollmentFlow_with_scope_and_claim.claims_eligibility_claim = ""
    # clean is OK
    model_EnrollmentFlow_with_scope_and_claim.clean()

    # reassign agency
    model_EnrollmentFlow_with_scope_and_claim.transit_agency = model_TransitAgency
    with pytest.raises(ValidationError) as e:
        model_EnrollmentFlow_with_scope_and_claim.clean()

    error_dict = e.value.error_dict
    assert "claims_scope" in error_dict
    assert "claims_eligibility_claim" in error_dict


@pytest.mark.django_db
def test_EnrollmentFlow_clean_eligibility_api_verification(model_EnrollmentFlow_with_eligibility_api, model_TransitAgency):
    # remove agency
    model_EnrollmentFlow_with_eligibility_api.transit_agency = None
    # and required fields
    model_EnrollmentFlow_with_eligibility_api.eligibility_api_auth_header = ""
    model_EnrollmentFlow_with_eligibility_api.eligibility_api_auth_key_secret_name = ""
    model_EnrollmentFlow_with_eligibility_api.eligibility_api_jwe_cek_enc = ""
    model_EnrollmentFlow_with_eligibility_api.eligibility_api_jwe_encryption_alg = ""
    model_EnrollmentFlow_with_eligibility_api.eligibility_api_jws_signing_alg = ""
    model_EnrollmentFlow_with_eligibility_api.eligibility_api_public_key = None
    model_EnrollmentFlow_with_eligibility_api.eligibility_api_url = ""
    model_EnrollmentFlow_with_eligibility_api.eligibility_form_class = ""
    # clean is OK
    model_EnrollmentFlow_with_eligibility_api.clean()

    # reassign agency
    model_EnrollmentFlow_with_eligibility_api.transit_agency = model_TransitAgency
    with pytest.raises(ValidationError) as e:
        model_EnrollmentFlow_with_eligibility_api.clean()

    error_dict = e.value.error_dict
    assert "eligibility_api_auth_header" in error_dict
    assert "eligibility_api_auth_key_secret_name" in error_dict
    assert "eligibility_api_jwe_cek_enc" in error_dict
    assert "eligibility_api_jwe_encryption_alg" in error_dict
    assert "eligibility_api_jws_signing_alg" in error_dict
    assert "eligibility_api_public_key" in error_dict
    assert "eligibility_api_url" in error_dict
    assert "eligibility_form_class" in error_dict


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

    model_EnrollmentFlow_supports_expiration.expiration_days = 0
    model_EnrollmentFlow_supports_expiration.expiration_reenrollment_days = 0
    model_EnrollmentFlow_supports_expiration.reenrollment_error_template = ""

    with pytest.raises(ValidationError) as e:
        model_EnrollmentFlow_supports_expiration.clean()

    error_dict = e.value.error_dict
    assert "expiration_days" in error_dict
    assert "expiration_reenrollment_days" in error_dict
    assert "reenrollment_error_template" in error_dict


@pytest.mark.django_db
@pytest.mark.parametrize(
    "template_attribute",
    [
        "selection_label_template_override",
        "eligibility_start_template_override",
        "eligibility_unverified_template_override",
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
def test_TransitProcessor_str(model_TransitProcessor):
    assert str(model_TransitProcessor) == model_TransitProcessor.name


@pytest.mark.django_db
def test_TransitAgency_defaults():
    agency = TransitAgency.objects.create(slug="test")

    assert agency.active is False
    assert agency.slug == "test"
    assert agency.short_name == ""
    assert agency.long_name == ""
    assert agency.phone == ""
    assert agency.info_url == ""
    assert agency.logo_large == ""
    assert agency.logo_small == ""
    # test fails if save fails
    agency.save()


@pytest.mark.django_db
def test_TransitAgency_str(model_TransitAgency):
    assert str(model_TransitAgency) == model_TransitAgency.long_name


@pytest.mark.django_db
def test_TransitAgency_template_overrides(model_TransitAgency):
    assert model_TransitAgency.index_template == model_TransitAgency.index_template_override
    assert model_TransitAgency.eligibility_index_template == model_TransitAgency.eligibility_index_template_override

    model_TransitAgency.index_template_override = ""
    model_TransitAgency.eligibility_index_template_override = ""
    model_TransitAgency.save()

    assert model_TransitAgency.index_template == f"core/index--{model_TransitAgency.slug}.html"
    assert model_TransitAgency.eligibility_index_template == f"eligibility/index--{model_TransitAgency.slug}.html"


@pytest.mark.django_db
def test_TransitAgency_index_url(model_TransitAgency):
    result = model_TransitAgency.index_url

    assert result.endswith(model_TransitAgency.slug)


@pytest.mark.django_db
def test_TransitAgency_by_id_matching(model_TransitAgency):
    result = TransitAgency.by_id(model_TransitAgency.id)

    assert result == model_TransitAgency


@pytest.mark.django_db
def test_TransitAgency_by_id_nonmatching():
    with pytest.raises(TransitAgency.DoesNotExist):
        TransitAgency.by_id(99999)


@pytest.mark.django_db
def test_TransitAgency_by_slug_matching(model_TransitAgency):
    result = TransitAgency.by_slug(model_TransitAgency.slug)

    assert result == model_TransitAgency


@pytest.mark.django_db
def test_TransitAgency_by_slug_nonmatching():
    result = TransitAgency.by_slug("nope")

    assert not result


@pytest.mark.django_db
def test_TransitAgency_all_active(model_TransitAgency):
    count = TransitAgency.objects.count()
    assert count >= 1

    inactive_agency = TransitAgency.by_id(model_TransitAgency.id)
    inactive_agency.pk = None
    inactive_agency.active = False
    inactive_agency.save()

    assert TransitAgency.objects.count() == count + 1

    result = TransitAgency.all_active()

    assert len(result) > 0
    assert model_TransitAgency in result
    assert inactive_agency not in result


@pytest.mark.django_db
def test_TransitAgency_for_user_in_group(model_TransitAgency):
    group = Group.objects.create(name="test_group")

    agency_for_user = TransitAgency.by_id(model_TransitAgency.id)
    agency_for_user.pk = None
    agency_for_user.staff_group = group
    agency_for_user.save()

    user = User.objects.create_user(username="test_user", email="test_user@example.com", password="test", is_staff=True)
    user.groups.add(group)

    assert TransitAgency.for_user(user) == agency_for_user


@pytest.mark.django_db
def test_TransitAgency_for_user_not_in_group(model_TransitAgency):
    group = Group.objects.create(name="test_group")

    agency_for_user = TransitAgency.by_id(model_TransitAgency.id)
    agency_for_user.pk = None
    agency_for_user.staff_group = group
    agency_for_user.save()

    user = User.objects.create_user(username="test_user", email="test_user@example.com", password="test", is_staff=True)

    assert TransitAgency.for_user(user) is None


@pytest.mark.django_db
def test_TransitAgency_for_user_in_group_not_linked_to_any_agency():
    group = Group.objects.create(name="another test group")

    user = User.objects.create_user(username="test_user", email="test_user@example.com", password="test", is_staff=True)
    user.groups.add(group)

    assert TransitAgency.for_user(user) is None


@pytest.mark.django_db
def test_agency_logo_small(model_TransitAgency):
    assert agency_logo_small(model_TransitAgency, "local_filename.png") == "agencies/test-sm.png"


@pytest.mark.django_db
def test_agency_logo_large(model_TransitAgency):
    assert agency_logo_large(model_TransitAgency, "local_filename.png") == "agencies/test-lg.png"


@pytest.mark.django_db
def test_TransitAgency_clean(model_TransitAgency_inactive, model_TransitProcessor):
    model_TransitAgency_inactive.transit_processor = model_TransitProcessor

    model_TransitAgency_inactive.short_name = ""
    model_TransitAgency_inactive.long_name = ""
    model_TransitAgency_inactive.phone = ""
    model_TransitAgency_inactive.info_url = ""
    model_TransitAgency_inactive.logo_large = ""
    model_TransitAgency_inactive.logo_small = ""
    model_TransitAgency_inactive.transit_processor_audience = ""
    model_TransitAgency_inactive.transit_processor_client_id = ""
    model_TransitAgency_inactive.transit_processor_client_secret_name = ""
    # agency is inactive, OK to have incomplete fields
    model_TransitAgency_inactive.clean()

    # now mark it active and expect failure on clean()
    model_TransitAgency_inactive.active = True
    with pytest.raises(ValidationError) as e:
        model_TransitAgency_inactive.clean()

    errors = e.value.error_dict

    assert "short_name" in errors
    assert "long_name" in errors
    assert "phone" in errors
    assert "info_url" in errors
    assert "logo_large" in errors
    assert "logo_small" in errors
    assert "transit_processor_audience" in errors
    assert "transit_processor_client_id" in errors
    assert "transit_processor_client_secret_name" in errors


@pytest.mark.django_db
@pytest.mark.parametrize("template_attribute", ["index_template_override", "eligibility_index_template_override"])
def test_TransitAgency_clean_templates(model_TransitAgency_inactive, template_attribute):
    setattr(model_TransitAgency_inactive, template_attribute, "does/not/exist.html")
    # agency is inactive, OK to have missing template
    model_TransitAgency_inactive.clean()

    # now mark it active and expect failure on clean()
    model_TransitAgency_inactive.active = True
    with pytest.raises(ValidationError, match="Template not found: does/not/exist.html"):
        model_TransitAgency_inactive.clean()


@pytest.mark.django_db
def test_TransitAgency_clean_dirty_flow(model_TransitAgency, model_EnrollmentFlow, model_ClaimsProvider):
    # partially setup the EnrollmentFlow
    # missing scope and claims
    model_EnrollmentFlow.claims_provider = model_ClaimsProvider
    model_EnrollmentFlow.transit_agency = model_TransitAgency

    # clean the agency, and expect an invalid EnrollmentFlow error
    with pytest.raises(ValidationError, match=f"Invalid EnrollmentFlow: {model_EnrollmentFlow.label}"):
        model_TransitAgency.clean()


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
