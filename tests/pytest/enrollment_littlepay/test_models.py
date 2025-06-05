from django.forms import ValidationError
import pytest

from benefits.core.models import Environment
from benefits.enrollment_littlepay.models import LittlepayConfig


@pytest.mark.django_db
def test_LittlepayConfig_defaults():
    littlepay_config = LittlepayConfig.objects.create(environment="qa", agency_slug="cst")

    assert littlepay_config.environment == "qa"
    assert littlepay_config.agency_slug == "cst"
    assert littlepay_config.audience == ""
    assert littlepay_config.client_id == ""
    assert littlepay_config.client_secret_name == ""
    # test fails if save fails
    littlepay_config.save()


@pytest.mark.django_db
def test_LittlepayConfig_str(model_LittlepayConfig):
    environment_label = Environment(model_LittlepayConfig.environment).label
    agency_slug = model_LittlepayConfig.agency_slug
    assert str(model_LittlepayConfig) == f"({environment_label}) {agency_slug}"


@pytest.mark.django_db
def test_LittlepayConfig_clean_inactive_agency(model_TransitAgency_inactive):
    littlepay_config = LittlepayConfig.objects.create(environment="qa", agency_slug="cst")
    littlepay_config.transitagency = model_TransitAgency_inactive
    littlepay_config.save()

    # test fails if clean fails
    littlepay_config.clean()

    # test fails if agency's clean fails
    model_TransitAgency_inactive.clean()


@pytest.mark.django_db
def test_LittlepayConfig_clean(model_TransitAgency_inactive):
    littlepay_config = LittlepayConfig.objects.create(environment="qa", agency_slug="cst")
    littlepay_config.transitagency = model_TransitAgency_inactive
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
