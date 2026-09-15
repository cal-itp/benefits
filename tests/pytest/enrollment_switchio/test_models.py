import pytest
from django.forms import ValidationError

from benefits.enrollment_switchio.models import SwitchioConfig, SwitchioGroup


@pytest.mark.django_db
def test_SwitchioConfig_defaults():
    switchio_config = SwitchioConfig.objects.create(environment="dev")

    assert switchio_config.environment == "dev"
    assert switchio_config.tokenization_api_key == ""
    assert switchio_config.tokenization_api_secret_name == ""
    assert switchio_config.pto_id == 0
    # test fails if save fails
    switchio_config.save()


@pytest.mark.django_db
def test_SwitchioConfig_clean_first_time_instance():
    # Simulate how Django Admin would call clean() on a new instance
    # first create a SwitchioConfig instance without saving it to the database
    switchio_config = SwitchioConfig(environment="dev")
    # then call clean() on it, which is what Django Admin does before saving
    # test fails if clean() fails
    switchio_config.clean()


@pytest.mark.django_db
def test_SwitchioConfig_clean_inactive_agency(model_TransitAgency_inactive):
    switchio_config = SwitchioConfig.objects.create(environment="dev")
    switchio_config.transit_agency = model_TransitAgency_inactive
    switchio_config.save()

    # test fails if clean fails
    switchio_config.clean()

    # test fails if agency's clean fails
    model_TransitAgency_inactive.clean()


@pytest.mark.django_db
def test_SwitchioConfig_clean(model_TransitAgency_inactive):
    switchio_config = SwitchioConfig.objects.create(environment="dev")
    switchio_config.save()
    model_TransitAgency_inactive.transit_processor_config = switchio_config
    model_TransitAgency_inactive.save()

    # agency is inactive, OK to have incomplete fields on agency's switchio_config
    model_TransitAgency_inactive.clean()

    # now mark it active and expect failure on clean()
    model_TransitAgency_inactive.active = True
    model_TransitAgency_inactive.save()

    with pytest.raises(ValidationError) as e:
        switchio_config.clean()

    errors = e.value.error_dict

    assert len(errors) == 3

    # the error_dict contains 3 items with the field name as the key mapped to a list of ValidationErrors
    for index, expected_key in [
        (0, "tokenization_api_key"),
        (1, "tokenization_api_secret_name"),
        (2, "pto_id"),
    ]:
        item = list(errors.items())[index]
        key, validation_errors = item
        error_message = validation_errors[0].message
        assert key == expected_key
        assert (
            error_message == "This field is required when this configuration is referenced by an active transit agency."
        )  # noqa


@pytest.mark.django_db
def test_SwitchioConfig_tokenization_api_base_url(mocker, model_SwitchioConfig):
    mocked_get_secret_by_name = mocker.patch(
        "benefits.enrollment_switchio.models.get_secret_by_name", return_value="secret url"
    )

    model_SwitchioConfig.tokenization_api_base_url

    mocked_get_secret_by_name.assert_called_once_with("switchio-tokenization-api-base-url")


@pytest.mark.django_db
def test_SwitchioConfig_enrollment_api_base_url(mocker, model_SwitchioConfig):
    mocked_get_secret_by_name = mocker.patch(
        "benefits.enrollment_switchio.models.get_secret_by_name", return_value="secret url"
    )

    model_SwitchioConfig.enrollment_api_base_url

    mocked_get_secret_by_name.assert_called_once_with("switchio-enrollment-api-base-url")


@pytest.mark.django_db
def test_SwitchioConfig_client_certificate_data(mocker, model_SwitchioConfig):
    mocked_get_secret_by_name = mocker.patch(
        "benefits.enrollment_switchio.models.get_secret_by_name", return_value="secret cert"
    )

    model_SwitchioConfig.client_certificate_data

    mocked_get_secret_by_name.assert_called_once_with("switchio-client-cert")


@pytest.mark.django_db
def test_SwitchioConfig_ca_certificate_data(mocker, model_SwitchioConfig):
    mocked_get_secret_by_name = mocker.patch(
        "benefits.enrollment_switchio.models.get_secret_by_name", return_value="secret cert"
    )

    model_SwitchioConfig.ca_certificate_data

    mocked_get_secret_by_name.assert_called_once_with("switchio-ca-cert")


@pytest.mark.django_db
def test_SwitchioConfig_private_key_data(mocker, model_SwitchioConfig):
    mocked_get_secret_by_name = mocker.patch(
        "benefits.enrollment_switchio.models.get_secret_by_name", return_value="secret cert"
    )

    model_SwitchioConfig.private_key_data

    mocked_get_secret_by_name.assert_called_once_with("switchio-private-key")


@pytest.mark.django_db
def test_SwitchioGroup_by_id_matching(model_SwitchioGroup):
    flow = SwitchioGroup.by_id(model_SwitchioGroup.id)

    assert flow == model_SwitchioGroup


@pytest.mark.django_db
def test_SwitchioGroup_by_id_nonmatching():
    with pytest.raises(SwitchioGroup.DoesNotExist):
        SwitchioGroup.by_id(99999)
