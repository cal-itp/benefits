from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS

import pytest

from benefits.routes import routes
from benefits.core.models import (
    TransitAgency,
    agency_logo_small,
    agency_logo_large,
)


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
    model_TransitAgency_inactive.switchio_config = None
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

    non_field_errors = errors[NON_FIELD_ERRORS]
    assert len(non_field_errors) == 1
    assert non_field_errors[0].message == "Must fill out configuration for either Littlepay or Switchio."


@pytest.mark.django_db
def test_TransitAgency_enrollment_index_route_littlepay(model_TransitAgency, model_LittlepayConfig):
    model_TransitAgency.littlepay_config = model_LittlepayConfig
    model_TransitAgency.switchio_config = None
    model_TransitAgency.save()

    assert model_TransitAgency.enrollment_index_route == routes.ENROLLMENT_LITTLEPAY_INDEX


@pytest.mark.django_db
def test_TransitAgency_enrollment_index_route_switchio(model_TransitAgency, model_SwitchioConfig):
    model_TransitAgency.littlepay_config = None
    model_TransitAgency.switchio_config = model_SwitchioConfig
    model_TransitAgency.save()

    assert model_TransitAgency.enrollment_index_route == routes.ENROLLMENT_SWITCHIO_INDEX


@pytest.mark.django_db
def test_TransitAgency_enrollment_index_route_no_config(model_TransitAgency):
    model_TransitAgency.littlepay_config = None
    model_TransitAgency.switchio_config = None
    model_TransitAgency.save()

    with pytest.raises(
        ValueError,
        match="TransitAgency must have either a LittlepayConfig or SwitchioConfig in order to show enrollment index.",
    ):
        model_TransitAgency.enrollment_index_route
