from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError

import pytest

from benefits.core.models import TransitAgency, Environment, LittlepayConfig, agency_logo_small, agency_logo_large


@pytest.mark.django_db
def test_TransitProcessor_str(model_TransitProcessor):
    assert str(model_TransitProcessor) == model_TransitProcessor.name


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
    inactive_agency.littlepay_config.pk = None
    inactive_agency.littlepay_config = inactive_agency.littlepay_config.save()
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
    agency_for_user.littlepay_config.pk = None
    agency_for_user.littlepay_config = agency_for_user.littlepay_config.save()
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
    agency_for_user.littlepay_config.pk = None
    agency_for_user.littlepay_config = agency_for_user.littlepay_config.save()
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
    assert agency_logo_small(model_TransitAgency, "local_filename.png") == "agencies/cst-sm.png"


@pytest.mark.django_db
def test_agency_logo_large(model_TransitAgency):
    assert agency_logo_large(model_TransitAgency, "local_filename.png") == "agencies/cst-lg.png"


@pytest.mark.django_db
def test_TransitAgency_clean(model_TransitAgency_inactive, model_TransitProcessor):
    model_TransitAgency_inactive.transit_processor = model_TransitProcessor

    model_TransitAgency_inactive.short_name = ""
    model_TransitAgency_inactive.long_name = ""
    model_TransitAgency_inactive.phone = ""
    model_TransitAgency_inactive.info_url = ""
    model_TransitAgency_inactive.logo_large = ""
    model_TransitAgency_inactive.logo_small = ""
    model_TransitAgency_inactive.littlepay_config = None
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
    assert "littlepay_config" in errors
