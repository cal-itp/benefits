from django.forms import ValidationError
import pytest

from benefits.enrollment_switchio.models import SwitchioConfig


@pytest.mark.django_db
def test_SwitchioConfig_defaults():
    switchio_config = SwitchioConfig.objects.create(environment="qa")

    assert switchio_config.environment == "qa"
    assert switchio_config.tokenization_api_key == ""
    assert switchio_config.tokenization_api_secret_name == ""
    assert switchio_config.enrollment_api_authorization_header == ""
    assert switchio_config.pto_id == 0
    assert switchio_config.client_certificate is None
    assert switchio_config.ca_certificate is None
    assert switchio_config.private_key is None
    # test fails if save fails
    switchio_config.save()


@pytest.mark.django_db
def test_SwitchioConfig_clean_inactive_agency(model_TransitAgency_inactive):
    switchio_config = SwitchioConfig.objects.create(
        environment="qa",
    )
    switchio_config.transitagency = model_TransitAgency_inactive
    switchio_config.save()

    # test fails if clean fails
    switchio_config.clean()

    # test fails if agency's clean fails
    model_TransitAgency_inactive.clean()


@pytest.mark.django_db
def test_SwitchioConfig_clean_create_from_agency():
    switchio_config = SwitchioConfig.objects.create(environment="qa")
    switchio_config.pk = None  # simulate admin form behavior, where we're creating the object from the TransitAgency.

    # test fails if clean() fails
    switchio_config.clean()


@pytest.mark.django_db
def test_SwitchioConfig_clean(model_TransitAgency_inactive):
    switchio_config = SwitchioConfig.objects.create(environment="qa")
    switchio_config.save()

    model_TransitAgency_inactive.switchio_config = switchio_config
    model_TransitAgency_inactive.save()

    # agency is inactive, OK to have incomplete fields on agency's switchio_config
    model_TransitAgency_inactive.clean()

    # now mark it active and expect failure on clean()
    model_TransitAgency_inactive.active = True
    model_TransitAgency_inactive.save()

    with pytest.raises(ValidationError) as e:
        model_TransitAgency_inactive.clean()

    errors = e.value.error_dict

    assert len(errors) == 1

    # the error_dict contains 1 item with key None to value of list of ValidationErrors
    item = list(errors.items())[0]
    key, validation_errors = item
    error_message = validation_errors[0].message
    assert (
        error_message
        == "Switchio configuration is missing fields that are required when this agency is active. Missing fields: tokenization_api_key, tokenization_api_secret_name, enrollment_api_authorization_header, pto_id, client_certificate, ca_certificate, private_key"  # noqa
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "environment, secret_name",
    [("qa", "switchio-qa-tokenization-api-base-url"), ("prod", "switchio-prod-tokenization-api-base-url")],
)
def test_SwitchioConfig_tokenization_api_base_url(mocker, environment, secret_name):
    switchio_config = SwitchioConfig.objects.create(environment=environment)
    mocked_get_secret_by_name = mocker.patch(
        "benefits.enrollment_switchio.models.get_secret_by_name", return_value="secret url"
    )

    switchio_config.tokenization_api_base_url

    mocked_get_secret_by_name.assert_called_once_with(secret_name)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "environment, secret_name",
    [("qa", "switchio-qa-enrollment-api-base-url"), ("prod", "switchio-prod-enrollment-api-base-url")],
)
def test_SwitchioConfig_enrollment_api_base_url(mocker, environment, secret_name):
    switchio_config = SwitchioConfig.objects.create(environment=environment)
    mocked_get_secret_by_name = mocker.patch(
        "benefits.enrollment_switchio.models.get_secret_by_name", return_value="secret url"
    )

    switchio_config.enrollment_api_base_url

    mocked_get_secret_by_name.assert_called_once_with(secret_name)


@pytest.mark.django_db
def test_SwitchioConfig_tokenization_api_base_url_unexpected_environment():
    environment = "unexpected-thiswillneverexist"
    switchio_config = SwitchioConfig.objects.create(environment=environment)

    with pytest.raises(ValueError, match=f"Unexpected value for environment: {environment}"):
        switchio_config.tokenization_api_base_url


@pytest.mark.django_db
def test_SwitchioConfig_enrollment_api_base_url_unexpected_environment():
    environment = "unexpected-thiswillneverexist"
    switchio_config = SwitchioConfig.objects.create(environment=environment)

    with pytest.raises(ValueError, match=f"Unexpected value for environment: {environment}"):
        switchio_config.enrollment_api_base_url
