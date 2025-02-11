from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError

import pytest

from benefits.core.models import TransitAgency, agency_logo_small, agency_logo_large


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
def test_TransitAgency_template_overrides(model_TransitAgency):
    assert model_TransitAgency.index_template == model_TransitAgency.index_template_override
    assert model_TransitAgency.eligibility_index_template == model_TransitAgency.eligibility_index_template_override

    model_TransitAgency.index_template_override = ""
    model_TransitAgency.eligibility_index_template_override = ""
    model_TransitAgency.save()

    assert model_TransitAgency.index_template == f"core/index--{model_TransitAgency.slug}.html"
    assert model_TransitAgency.eligibility_index_template == f"eligibility/index--{model_TransitAgency.slug}.html"


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
def test_agency_logo_small(model_TransitAgency):
    assert agency_logo_small(model_TransitAgency, "local_filename.png") == "agencies/test-sm.png"


@pytest.mark.django_db
def test_agency_logo_large(model_TransitAgency):
    assert agency_logo_large(model_TransitAgency, "local_filename.png") == "agencies/test-lg.png"


@pytest.mark.django_db
def test_TransitAgency_clean(model_TransitAgency_inactive, model_TransitProcessor):
    model_TransitAgency_inactive.transit_processor = model_TransitProcessor

    model_TransitAgency_inactive.short_name = ""
    model_TransitAgency_inactive.long_name = ""
    model_TransitAgency_inactive.phone = ""
    model_TransitAgency_inactive.info_url = ""
    model_TransitAgency_inactive.logo_large = ""
    model_TransitAgency_inactive.logo_small = ""
    model_TransitAgency_inactive.transit_processor_audience = ""
    model_TransitAgency_inactive.transit_processor_client_id = ""
    model_TransitAgency_inactive.transit_processor_client_secret_name = ""
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
    assert "transit_processor_audience" in errors
    assert "transit_processor_client_id" in errors
    assert "transit_processor_client_secret_name" in errors


@pytest.mark.django_db
@pytest.mark.parametrize("template_attribute", ["index_template_override", "eligibility_index_template_override"])
def test_TransitAgency_clean_templates(model_TransitAgency_inactive, template_attribute):
    setattr(model_TransitAgency_inactive, template_attribute, "does/not/exist.html")
    # agency is inactive, OK to have missing template
    model_TransitAgency_inactive.clean()

    # now mark it active and expect failure on clean()
    model_TransitAgency_inactive.active = True
    with pytest.raises(ValidationError, match="Template not found: does/not/exist.html"):
        model_TransitAgency_inactive.clean()
