from django.forms import ValidationError
import pytest

from benefits.enrollment_littlepay.models import LittlepayConfig


@pytest.mark.django_db
def test_LittlepayConfig_defaults():
    littlepay_config = LittlepayConfig.objects.create(environment="qa")

    assert littlepay_config.environment == "qa"
    assert littlepay_config.audience == ""
    assert littlepay_config.client_id == ""
    assert littlepay_config.client_secret_name == ""
    # test fails if save fails
    littlepay_config.save()


@pytest.mark.django_db
def test_LittlepayConfig_clean_inactive_agency(model_TransitAgency_inactive):
    littlepay_config = LittlepayConfig.objects.create(environment="qa")
    littlepay_config.transit_agency = model_TransitAgency_inactive
    littlepay_config.save()

    # test fails if clean fails
    littlepay_config.clean()

    # test fails if agency's clean fails
    model_TransitAgency_inactive.clean()


@pytest.mark.django_db
def test_LittlepayConfig_clean(model_TransitAgency_inactive):
    littlepay_config = LittlepayConfig.objects.create(environment="qa")
    littlepay_config.transit_agency = model_TransitAgency_inactive
    littlepay_config.save()

    # agency is inactive, OK to have incomplete fields on agency's littlepay_config
    model_TransitAgency_inactive.clean()

    # now mark it active and expect failure on clean()
    model_TransitAgency_inactive.active = True
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
        == "Littlepay configuration is missing fields that are required when this agency is active. Missing fields: audience, client_id, client_secret_name"  # noqa
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "environment, secret_name", [("qa", "littlepay-qa-api-base-url"), ("prod", "littlepay-prod-api-base-url")]
)
def test_LittlepayConfig_api_base_url(mocker, environment, secret_name):
    littlepay_config = LittlepayConfig.objects.create(environment=environment)
    mocked_get_secret_by_name = mocker.patch(
        "benefits.enrollment_littlepay.models.get_secret_by_name", return_value="secret url"
    )

    littlepay_config.api_base_url

    mocked_get_secret_by_name.assert_called_once_with(secret_name)


@pytest.mark.django_db
def test_LittlepayConfig_api_base_url_unexpected_environment():
    environment = "unexpected-thiswillneverexist"
    littlepay_config = LittlepayConfig.objects.create(environment=environment)

    with pytest.raises(ValueError, match=f"Unexpected value for environment: {environment}"):
        littlepay_config.api_base_url
