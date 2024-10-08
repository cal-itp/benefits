from datetime import timedelta
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.utils import timezone

import pytest

from benefits.core.models import SecretNameField, EnrollmentFlow, TransitAgency, EnrollmentEvent, EnrollmentMethods
import benefits.secrets


@pytest.fixture
def mock_requests_get_pem_data(mocker):
    # intercept and spy on the GET request
    return mocker.patch("benefits.core.models.requests.get", return_value=mocker.Mock(text="PEM text"))


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
def test_EnrollmentFlow_supports_expiration_False(model_EnrollmentFlow, model_EnrollmentFlow_does_not_support_expiration):
    # test will fail if any error is raised
    model_EnrollmentFlow_does_not_support_expiration.full_clean()


@pytest.mark.django_db
def test_EnrollmentFlow_zero_expiration_days(model_EnrollmentFlow_zero_expiration_days):
    with pytest.raises(ValidationError) as exception_info:
        model_EnrollmentFlow_zero_expiration_days.full_clean()

    error_dict = exception_info.value.error_dict
    assert len(error_dict["expiration_days"]) == 1
    assert error_dict["expiration_days"][0].message == "When support_expiration is True, this value must be greater than 0."


@pytest.mark.django_db
def test_EnrollmentFlow_zero_expiration_reenrollment_days(model_EnrollmentFlow_zero_expiration_reenrollment_days):
    with pytest.raises(ValidationError) as exception_info:
        model_EnrollmentFlow_zero_expiration_reenrollment_days.full_clean()

    error_dict = exception_info.value.error_dict
    assert len(error_dict["expiration_reenrollment_days"]) == 1
    assert (
        error_dict["expiration_reenrollment_days"][0].message
        == "When support_expiration is True, this value must be greater than 0."
    )


@pytest.mark.django_db
def test_EnrollmentFlow_missing_reenrollment_template(model_EnrollmentFlow_supports_expiration):
    model_EnrollmentFlow_supports_expiration.reenrollment_error_template = None
    model_EnrollmentFlow_supports_expiration.save()

    with pytest.raises(ValidationError) as exception_info:
        model_EnrollmentFlow_supports_expiration.full_clean()

    error_dict = exception_info.value.error_dict
    assert len(error_dict["reenrollment_error_template"]) == 1
    assert error_dict["reenrollment_error_template"][0].message == "Required when supports expiration is True."


@pytest.mark.django_db
def test_EnrollmentFlow_supports_expiration(model_EnrollmentFlow_supports_expiration):
    # test will fail if any error is raised
    model_EnrollmentFlow_supports_expiration.full_clean()


@pytest.mark.django_db
def test_EnrollmentFlow_enrollment_index_template(model_TransitAgency):
    new_flow = EnrollmentFlow.objects.create(transit_agency=model_TransitAgency)

    assert new_flow.enrollment_index_template == "enrollment/index.html"

    new_flow.enrollment_index_template = "test/enrollment.html"
    new_flow.save()

    assert new_flow.enrollment_index_template == "test/enrollment.html"


@pytest.mark.django_db
def test_EnrollmentFlow_enrollment_success_template(model_TransitAgency):
    new_flow = EnrollmentFlow.objects.create(transit_agency=model_TransitAgency)

    assert new_flow.enrollment_success_template == "enrollment/success.html"


@pytest.mark.django_db
def test_EnrollmentFlow_supported_enrollment_methods(model_TransitAgency):
    new_flow = EnrollmentFlow.objects.create(transit_agency=model_TransitAgency)

    assert new_flow.supported_enrollment_methods == ["digital", "in_person"]


class SampleFormClass:
    """A class for testing EligibilityVerificationForm references."""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


@pytest.mark.django_db
def test_EnrollmentFlow_eligibility_start_template(model_EnrollmentFlow):
    assert model_EnrollmentFlow.eligibility_start_template == "eligibility/start.html"


@pytest.mark.django_db
def test_EnrollmentFlow_eligibility_form_instance(model_EnrollmentFlow):
    model_EnrollmentFlow.eligibility_form_class = f"{__name__}.SampleFormClass"
    model_EnrollmentFlow.save()

    args = (1, "2")
    kwargs = {"one": 1, "two": "2"}
    form_instance = model_EnrollmentFlow.eligibility_form_instance(*args, **kwargs)

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
def test_EnrollmentFlow_no_scope_and_claim(model_EnrollmentFlow):

    assert not model_EnrollmentFlow.uses_claims_verification


@pytest.mark.django_db
def test_EnrollmentFlow_no_scope_and_claim_no_sign_out(model_EnrollmentFlow, model_ClaimsProvider_no_sign_out):
    model_EnrollmentFlow.claims_provider = model_ClaimsProvider_no_sign_out

    assert not model_EnrollmentFlow.uses_claims_verification


@pytest.mark.django_db
def test_EnrollmentFlow_eligibility_api(model_EnrollmentFlow_with_eligibility_api):
    assert (
        model_EnrollmentFlow_with_eligibility_api.eligibility_verifier
        == model_EnrollmentFlow_with_eligibility_api.eligibility_api_url
    )


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
def test_EnrollmentFlow_with_claims_scheme(model_EnrollmentFlow_with_claims_scheme):
    assert model_EnrollmentFlow_with_claims_scheme.claims_scheme == "scheme"


@pytest.mark.django_db
def test_TransitProcessor_str(model_TransitProcessor):
    assert str(model_TransitProcessor) == model_TransitProcessor.name


@pytest.mark.django_db
def test_TransitAgency_str(model_TransitAgency):
    assert str(model_TransitAgency) == model_TransitAgency.long_name


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
