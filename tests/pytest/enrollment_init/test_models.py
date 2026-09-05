import pytest
from django.forms import ValidationError

from benefits.core.models import SecretNameField
from benefits.enrollment_init.models import InitConfig


@pytest.mark.django_db
def test_InitConfig_defaults():
    init_config = InitConfig.objects.create(environment="dev")

    assert init_config.environment == "dev"

    # test fails if save fails
    init_config.save()


@pytest.mark.django_db
def test_InitConfig_clean_first_time_instance():
    # Simulate how Django Admin would call clean() on a new instance
    # first create a InitConfig instance without saving it to the database
    init_config = InitConfig(environment="dev")
    init_config.tokenization_api_key = "apikey"
    # then call clean() on it, which is what Django Admin does before saving
    # test fails if clean() fails
    init_config.clean()


@pytest.mark.django_db
def test_InitConfig_clean():
    init_config = InitConfig.objects.create(environment="dev")
    init_config.save()

    with pytest.raises(ValidationError) as e:
        init_config.clean()

    errors = e.value.error_dict

    assert len(errors) == 1

    # the error_dict contains 1 item with key None to value of list of ValidationErrors
    item = list(errors.items())[0]
    key, validation_errors = item
    error_message = validation_errors[0].message
    assert key == "tokenization_api_key"
    assert error_message == "This field is required when this configuration is referenced by an active transit agency."  # noqa


@pytest.mark.django_db
def test_InitConfig_registration_password(mocker, model_InitConfig):
    pw = "P@ssword123"
    mocked_secret_value = mocker.patch.object(SecretNameField, "secret_value", return_value=pw)

    result = model_InitConfig.registration_password

    assert result == pw
    mocked_secret_value.assert_called_once_with(model_InitConfig)
