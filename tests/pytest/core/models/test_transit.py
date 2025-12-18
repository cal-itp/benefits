from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS

import pytest

from benefits.routes import routes
from benefits.core.models import (
    CardSchemes,
    Environment,
    TransitAgency,
    TransitProcessorConfig,
    agency_logo,
)


class TestCardSchemes:
    def test_choice_order(self):
        expected_order = [CardSchemes.VISA, CardSchemes.MASTERCARD, CardSchemes.DISCOVER, CardSchemes.AMEX]
        assert list(CardSchemes.CHOICES.keys()) == expected_order


@pytest.mark.django_db
def test_TransitProcessorConfig_str(model_TransitAgency):
    transit_processor_config = TransitProcessorConfig.objects.create(environment="qa", transit_agency=model_TransitAgency)
    environment_label = Environment(transit_processor_config.environment).label
    agency_slug = transit_processor_config.transit_agency.slug
    assert str(transit_processor_config) == f"({environment_label}) {agency_slug}"


@pytest.mark.django_db
def test_TransitAgency_defaults():
    agency = TransitAgency.objects.create(slug="test")

    assert agency.active is False
    assert agency.slug == "test"
    assert agency.short_name == ""
    assert agency.long_name == ""
    assert agency.phone == ""
    assert agency.supported_card_schemes == [CardSchemes.VISA, CardSchemes.MASTERCARD]
    assert agency.info_url == ""
    assert agency.logo == ""
    # test fails if save fails
    agency.save()


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
    agency_for_user.customer_service_group = group
    agency_for_user.save()

    user = User.objects.create_user(username="test_user", email="test_user@example.com", password="test", is_staff=True)
    user.groups.add(group)

    assert TransitAgency.for_user(user) == agency_for_user


@pytest.mark.django_db
def test_TransitAgency_for_user_not_in_group(model_TransitAgency):
    group = Group.objects.create(name="test_group")

    agency_for_user = TransitAgency.by_id(model_TransitAgency.id)
    agency_for_user.pk = None
    agency_for_user.customer_service_group = group
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
def test_agency_logo(model_TransitAgency):
    assert agency_logo(model_TransitAgency, "local_filename.png") == "agencies/cst.png"


@pytest.mark.django_db
def test_TransitAgency_clean(model_TransitAgency_inactive):
    model_TransitAgency_inactive.long_name = ""
    model_TransitAgency_inactive.phone = ""
    model_TransitAgency_inactive.info_url = ""
    model_TransitAgency_inactive.logo = ""
    # agency is inactive, OK to have incomplete fields
    model_TransitAgency_inactive.clean()

    # now mark it active and expect failure on clean()
    model_TransitAgency_inactive.active = True
    with pytest.raises(ValidationError) as e:
        model_TransitAgency_inactive.clean()

    errors = e.value.error_dict

    assert "long_name" in errors
    assert "phone" in errors
    assert "info_url" in errors
    assert "logo" in errors

    non_field_errors = errors[NON_FIELD_ERRORS]
    assert len(non_field_errors) == 1
    assert non_field_errors[0].message == "Must fill out configuration for either Littlepay or Switchio."


@pytest.mark.django_db
def test_TransitAgency_clean_short_name_change_requires_group(model_TransitAgency_inactive):
    group = Group.objects.create(name="Existing Customer Service Group")
    model_TransitAgency_inactive.customer_service_group = group
    model_TransitAgency_inactive.save()

    # change the short name and assign no group
    model_TransitAgency_inactive.short_name = "NEW"
    model_TransitAgency_inactive.customer_service_group = None

    with pytest.raises(ValidationError) as e:
        model_TransitAgency_inactive.clean()

    errors = e.value.error_dict
    assert "customer_service_group" in errors
    assert "Blank not allowed. Set to its original value if changing the Short Name." in str(errors["customer_service_group"])


@pytest.mark.django_db
def test_TransitAgency_transit_processor_littlepay(model_TransitAgency, model_LittlepayConfig):
    model_LittlepayConfig.transit_agency = model_TransitAgency
    model_TransitAgency.save()

    assert model_TransitAgency.transit_processor == "littlepay"


@pytest.mark.django_db
def test_TransitAgency_transit_processor_switchio(model_TransitAgency, model_SwitchioConfig):
    model_SwitchioConfig.transit_agency = model_TransitAgency
    model_TransitAgency.save()

    assert model_TransitAgency.transit_processor == "switchio"


@pytest.mark.django_db
def test_TransitAgency_transit_processor_no_config(model_TransitAgency):
    assert model_TransitAgency.transit_processor is None


@pytest.mark.django_db
def test_TransitAgency_enrollment_index_route_littlepay(model_TransitAgency, model_LittlepayConfig):
    model_LittlepayConfig.transit_agency = model_TransitAgency
    model_TransitAgency.save()

    assert model_TransitAgency.enrollment_index_route == routes.ENROLLMENT_LITTLEPAY_INDEX


@pytest.mark.django_db
def test_TransitAgency_enrollment_index_route_switchio(model_TransitAgency, model_SwitchioConfig):
    model_SwitchioConfig.transit_agency = model_TransitAgency
    model_TransitAgency.save()

    assert model_TransitAgency.enrollment_index_route == routes.ENROLLMENT_SWITCHIO_INDEX


@pytest.mark.django_db
def test_TransitAgency_enrollment_index_route_no_config(model_TransitAgency):
    with pytest.raises(
        ValueError,
        match="TransitAgency must have either a LittlepayConfig or SwitchioConfig in order to show enrollment index.",
    ):
        model_TransitAgency.enrollment_index_route


@pytest.mark.django_db
def test_TransitAgency_in_person_enrollment_index_route_littlepay(model_TransitAgency, model_LittlepayConfig):
    model_LittlepayConfig.transit_agency = model_TransitAgency
    model_TransitAgency.save()

    assert model_TransitAgency.in_person_enrollment_index_route == routes.IN_PERSON_ENROLLMENT_LITTLEPAY_INDEX


@pytest.mark.django_db
def test_TransitAgency_in_person_enrollment_index_route_switchio(model_TransitAgency, model_SwitchioConfig):
    model_SwitchioConfig.transit_agency = model_TransitAgency
    model_TransitAgency.save()

    assert model_TransitAgency.in_person_enrollment_index_route == routes.IN_PERSON_ENROLLMENT_SWITCHIO_INDEX


@pytest.mark.django_db
def test_TransitAgency_in_person_enrollment_index_route_no_config(model_TransitAgency):
    with pytest.raises(
        ValueError,
        match=(
            "TransitAgency must have either a LittlepayConfig or SwitchioConfig "
            "in order to show in-person enrollment index."
        ),
    ):
        model_TransitAgency.in_person_enrollment_index_route
