from django.conf import settings

import pytest

from benefits.core.models import SecretNameField, EligibilityType, EligibilityVerifier, TransitAgency
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
def test_model_AuthProvider(model_AuthProvider):
    assert not model_AuthProvider.supports_claims_verification
    assert model_AuthProvider.supports_sign_out


@pytest.mark.django_db
def test_model_AuthProvider_client_id(model_AuthProvider, mock_models_get_secret_by_name):
    secret_value = model_AuthProvider.client_id

    mock_models_get_secret_by_name.assert_called_once_with(model_AuthProvider.client_id_secret_name)
    assert secret_value == mock_models_get_secret_by_name.return_value


@pytest.mark.django_db
def test_model_AuthProvider_with_verification(model_AuthProvider_with_verification):
    assert model_AuthProvider_with_verification.supports_claims_verification


@pytest.mark.django_db
def test_model_AuthProvider_with_verification_no_sign_out(model_AuthProvider_with_verification_no_sign_out):
    assert model_AuthProvider_with_verification_no_sign_out.supports_claims_verification
    assert not model_AuthProvider_with_verification_no_sign_out.supports_sign_out


@pytest.mark.django_db
def test_model_AuthProvider_without_verification(model_AuthProvider_without_verification):
    assert not model_AuthProvider_without_verification.supports_claims_verification


@pytest.mark.django_db
def test_model_AuthProvider_without_verification_no_sign_out(model_AuthProvider_without_verification_no_sign_out):
    assert not model_AuthProvider_without_verification_no_sign_out.supports_claims_verification
    assert not model_AuthProvider_without_verification_no_sign_out.supports_sign_out


@pytest.mark.django_db
def test_model_EligibilityType_str(model_EligibilityType):
    assert str(model_EligibilityType) == model_EligibilityType.label


@pytest.mark.django_db
def test_EligibilityType_get_matching(model_EligibilityType):
    eligibility = EligibilityType.get(model_EligibilityType.id)

    assert eligibility == model_EligibilityType


@pytest.mark.django_db
def test_EligibilityType_get_nonmatching():
    with pytest.raises(EligibilityType.DoesNotExist):
        EligibilityType.get(99999)


@pytest.mark.django_db
def test_EligibilityType_get_many_matching(model_EligibilityType):
    new_type = EligibilityType.get(model_EligibilityType.id)
    new_type.pk = None
    new_type.save()

    result = EligibilityType.get_many([model_EligibilityType.id, new_type.id])

    assert len(result) == 2
    assert model_EligibilityType in result
    assert new_type in result


@pytest.mark.django_db
def test_EligibilityType_get_many_nonmatching():
    result = EligibilityType.get_many([99998, 99999])

    assert len(result) == 0


@pytest.mark.django_db
def test_EligibilityType_get_many_somematching(model_EligibilityType):
    result = EligibilityType.get_many([model_EligibilityType.id, 99999])

    assert len(result) == 1
    assert model_EligibilityType in result


@pytest.mark.django_db
def test_EligibilityType_get_names(model_EligibilityType):
    expected = [model_EligibilityType.name]

    result = EligibilityType.get_names([model_EligibilityType])

    assert result == expected


@pytest.mark.django_db
def test_EligibilityVerifier_str(model_EligibilityVerifier):
    assert str(model_EligibilityVerifier) == model_EligibilityVerifier.name


class SampleFormClass:
    """A class for testing EligibilityVerifier form references."""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


@pytest.mark.django_db
def test_EligibilityVerifier_form_instance(model_EligibilityVerifier):
    model_EligibilityVerifier.form_class = f"{__name__}.SampleFormClass"
    model_EligibilityVerifier.save()

    args = (1, "2")
    kwargs = {"one": 1, "two": "2"}
    form_instance = model_EligibilityVerifier.form_instance(*args, **kwargs)

    assert isinstance(form_instance, SampleFormClass)
    assert form_instance.args == args
    assert form_instance.kwargs == kwargs


@pytest.mark.django_db
def test_EligibilityVerifier_by_id_matching(model_EligibilityVerifier):
    verifier = EligibilityVerifier.by_id(model_EligibilityVerifier.id)

    assert verifier == model_EligibilityVerifier


@pytest.mark.django_db
def test_EligibilityVerifier_by_id_nonmatching():
    with pytest.raises(EligibilityVerifier.DoesNotExist):
        EligibilityVerifier.by_id(99999)


@pytest.mark.django_db
def test_EligibilityVerifier_with_AuthProvider_with_verification(
    model_EligibilityVerifier, model_AuthProvider_with_verification
):
    model_EligibilityVerifier.auth_provider = model_AuthProvider_with_verification

    assert model_EligibilityVerifier.is_auth_required
    assert model_EligibilityVerifier.uses_auth_verification


@pytest.mark.django_db
def test_EligibilityVerifier_with_AuthProvider_with_verification_no_sign_out(
    model_EligibilityVerifier, model_AuthProvider_with_verification_no_sign_out
):
    model_EligibilityVerifier.auth_provider = model_AuthProvider_with_verification_no_sign_out

    assert model_EligibilityVerifier.is_auth_required
    assert model_EligibilityVerifier.uses_auth_verification


@pytest.mark.django_db
def test_EligibilityVerifier_with_AuthProvider_without_verification(
    model_EligibilityVerifier, model_AuthProvider_without_verification
):
    model_EligibilityVerifier.auth_provider = model_AuthProvider_without_verification

    assert model_EligibilityVerifier.is_auth_required
    assert not model_EligibilityVerifier.uses_auth_verification


@pytest.mark.django_db
def test_EligibilityVerifier_with_AuthProvider_without_verification_no_sign_out(
    model_EligibilityVerifier, model_AuthProvider_without_verification_no_sign_out
):
    model_EligibilityVerifier.auth_provider = model_AuthProvider_without_verification_no_sign_out

    assert model_EligibilityVerifier.is_auth_required
    assert not model_EligibilityVerifier.uses_auth_verification


@pytest.mark.django_db
def test_EligibilityVerifier_without_AuthProvider(model_EligibilityVerifier):
    model_EligibilityVerifier.auth_provider = None

    assert not model_EligibilityVerifier.is_auth_required
    assert not model_EligibilityVerifier.uses_auth_verification


@pytest.mark.django_db
def test_EligiblityVerifier_api_auth_key(model_EligibilityVerifier, mock_models_get_secret_by_name):
    secret_value = model_EligibilityVerifier.api_auth_key

    mock_models_get_secret_by_name.assert_called_once_with(model_EligibilityVerifier.api_auth_key_secret_name)
    assert secret_value == mock_models_get_secret_by_name.return_value


@pytest.mark.django_db
def test_PaymentProcessor_str(model_PaymentProcessor):
    assert str(model_PaymentProcessor) == model_PaymentProcessor.name


@pytest.mark.django_db
def test_TransitAgency_str(model_TransitAgency):
    assert str(model_TransitAgency) == model_TransitAgency.long_name


@pytest.mark.django_db
def test_TransitAgency_get_type_id_matching(model_TransitAgency):
    eligibility = model_TransitAgency.eligibility_types.first()
    result = model_TransitAgency.get_type_id(eligibility.name)

    assert result == eligibility.id


@pytest.mark.django_db
def test_TransitAgency_get_type_id_manymatching(model_TransitAgency):
    eligibility = model_TransitAgency.eligibility_types.first()
    new_eligibility = EligibilityType.get(eligibility.id)
    new_eligibility.pk = None
    new_eligibility.save()
    model_TransitAgency.eligibility_types.add(new_eligibility)

    with pytest.raises(Exception, match=r"name"):
        model_TransitAgency.get_type_id(eligibility.name)


@pytest.mark.django_db
def test_TransitAgency_get_type_id_nonmatching(model_TransitAgency):
    with pytest.raises(Exception, match=r"name"):
        model_TransitAgency.get_type_id("something")


@pytest.mark.django_db
def test_TransitAgency_supports_type_matching(model_TransitAgency):
    eligibility = model_TransitAgency.eligibility_types.first()

    assert model_TransitAgency.supports_type(eligibility)


@pytest.mark.django_db
def test_TransitAgency_supports_type_nonmatching(model_TransitAgency):
    eligibility = model_TransitAgency.eligibility_types.first()
    new_eligibility = EligibilityType.get(eligibility.id)
    new_eligibility.pk = None
    new_eligibility.save()

    assert not model_TransitAgency.supports_type(new_eligibility)


@pytest.mark.django_db
def test_TransitAgency_supports_type_wrongtype(model_TransitAgency):
    eligibility = model_TransitAgency.eligibility_types.first()

    assert not model_TransitAgency.supports_type(eligibility.name)


@pytest.mark.django_db
def test_TransitAgency_types_to_verify(model_TransitAgency):
    eligibility = model_TransitAgency.eligibility_types.first()
    new_eligibility = EligibilityType.get(eligibility.id)
    new_eligibility.pk = None
    new_eligibility.save()

    assert eligibility != new_eligibility

    model_TransitAgency.eligibility_types.add(new_eligibility)
    assert model_TransitAgency.eligibility_types.count() == 2

    verifier = model_TransitAgency.eligibility_verifiers.first()
    assert verifier.eligibility_type == eligibility

    result = model_TransitAgency.types_to_verify(verifier)
    assert len(result) == 1
    assert eligibility in result


@pytest.mark.django_db
def test_TransitAgency_type_names_to_verify(model_TransitAgency, model_EligibilityVerifier):
    expected = [t.name for t in model_TransitAgency.types_to_verify(model_EligibilityVerifier)]

    result = model_TransitAgency.type_names_to_verify(model_EligibilityVerifier)

    assert result == expected


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
