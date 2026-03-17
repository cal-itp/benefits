import pytest
from django.contrib.auth.models import Group, User
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError

from benefits.core.models import (
    CardSchemes,
    Environment,
    TransitAgency,
    TransitAgencyGroup,
    TransitProcessorConfig,
    agency_logo,
)
from benefits.routes import routes


@pytest.fixture
def model_TransitAgency_2():
    agency = TransitAgency.objects.create(
        slug="cst2",
        short_name="TEST 2",
        long_name="Test Transit Agency 2",
        info_url="https://example.com/test-agency-2",
        phone="800-555-5556",
        active=True,
        logo="agencies/cst.png",
    )

    return agency


@pytest.fixture()
def model_TransitAgencyGroup(model_TransitAgency, model_TransitAgency_2):
    group = TransitAgencyGroup.objects.create(label="group")
    group.transit_agencies.add(model_TransitAgency, model_TransitAgency_2)
    group.save()

    return group


class TestCardSchemes:
    def test_choice_order(self):
        expected_order = [CardSchemes.VISA, CardSchemes.MASTERCARD, CardSchemes.DISCOVER, CardSchemes.AMEX]
        assert list(CardSchemes.CHOICES.keys()) == expected_order


@pytest.mark.django_db
def test_TransitProcessorConfig_str():
    label = "cst"
    transit_processor_config = TransitProcessorConfig.objects.create(environment="dev", label=label)
    environment_label = Environment(transit_processor_config.environment).label

    assert str(transit_processor_config) == f"({environment_label}) {label}"


@pytest.mark.django_db
class TestTransitAgency:
    def test_defaults(self):
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

    def test_str(self, model_TransitAgency):
        assert str(model_TransitAgency) == model_TransitAgency.long_name

    def test_str__falls_back_to_short_name(self, model_TransitAgency):
        model_TransitAgency.long_name = ""
        model_TransitAgency.save()

        assert str(model_TransitAgency) == model_TransitAgency.short_name

    def test_index_url(self, model_TransitAgency):
        result = model_TransitAgency.index_url

        assert result.endswith(model_TransitAgency.slug)

    def test_by_id_matching(self, model_TransitAgency):
        result = TransitAgency.by_id(model_TransitAgency.id)

        assert result == model_TransitAgency

    def test_by_id_nonmatching(
        self,
    ):
        with pytest.raises(TransitAgency.DoesNotExist):
            TransitAgency.by_id(99999)

    def test_by_slug_matching(self, model_TransitAgency):
        result = TransitAgency.by_slug(model_TransitAgency.slug)

        assert result == model_TransitAgency

    def test_by_slug_nonmatching(
        self,
    ):
        result = TransitAgency.by_slug("nope")

        assert not result

    def test_all_active(self, model_TransitAgency):
        count = TransitAgency.objects.count()
        assert count >= 1

        inactive_agency = TransitAgency.by_id(model_TransitAgency.id)
        inactive_agency.pk = None
        inactive_agency.slug = "abc"
        inactive_agency.active = False
        inactive_agency.save()

        assert TransitAgency.objects.count() == count + 1

        result = TransitAgency.all_active()

        assert len(result) > 0
        assert model_TransitAgency in result
        assert inactive_agency not in result

    def test_for_user_in_group(self, model_TransitAgency):
        group = Group.objects.create(name="test_group")

        agency_for_user = TransitAgency.by_id(model_TransitAgency.id)
        agency_for_user.customer_service_group = group
        agency_for_user.save()

        user = User.objects.create_user(username="test_user", email="test_user@example.com", password="test", is_staff=True)
        user.groups.add(group)

        assert TransitAgency.for_user(user) == agency_for_user

    def test_for_user_not_in_group(self, model_TransitAgency):
        group = Group.objects.create(name="test_group")

        agency_for_user = TransitAgency.by_id(model_TransitAgency.id)
        agency_for_user.customer_service_group = group
        agency_for_user.save()

        user = User.objects.create_user(username="test_user", email="test_user@example.com", password="test", is_staff=True)

        assert TransitAgency.for_user(user) is None

    def test_for_user_in_group_not_linked_to_any_agency(
        self,
    ):
        group = Group.objects.create(name="another test group")

        user = User.objects.create_user(username="test_user", email="test_user@example.com", password="test", is_staff=True)
        user.groups.add(group)

        assert TransitAgency.for_user(user) is None

    def test_agency_logo(self, model_TransitAgency):
        assert agency_logo(model_TransitAgency, "local_filename.png") == "agencies/cst.png"

    def test_clean(self, model_TransitAgency_inactive):
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

    def test_clean_short_name_change_requires_group(self, model_TransitAgency_inactive):
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
        assert "Blank not allowed. Set to its original value if changing the Short Name." in str(
            errors["customer_service_group"]
        )

    def test_transit_processor_littlepay(self, model_TransitAgency, model_LittlepayConfig):
        model_LittlepayConfig.transit_agency = model_TransitAgency
        model_TransitAgency.save()

        assert model_TransitAgency.transit_processor == "littlepay"

    def test_transit_processor_switchio(self, model_TransitAgency, model_SwitchioConfig):
        model_SwitchioConfig.transit_agency = model_TransitAgency
        model_TransitAgency.save()

        assert model_TransitAgency.transit_processor == "switchio"

    def test_transit_processor_no_config(self, model_TransitAgency):
        assert model_TransitAgency.transit_processor is None

    def test_enrollment_index_route_littlepay(self, model_TransitAgency, model_LittlepayConfig):
        model_LittlepayConfig.transit_agency = model_TransitAgency
        model_TransitAgency.save()

        assert model_TransitAgency.enrollment_index_route == routes.ENROLLMENT_LITTLEPAY_INDEX

    def test_enrollment_index_route_switchio(self, model_TransitAgency, model_SwitchioConfig):
        model_SwitchioConfig.transit_agency = model_TransitAgency
        model_TransitAgency.save()

        assert model_TransitAgency.enrollment_index_route == routes.ENROLLMENT_SWITCHIO_INDEX

    def test_enrollment_index_route_no_config(self, model_TransitAgency):
        with pytest.raises(
            ValueError,
            match="TransitAgency must have either a LittlepayConfig or SwitchioConfig in order to show enrollment index.",
        ):
            model_TransitAgency.enrollment_index_route

    def test_in_person_enrollment_index_route_littlepay(self, model_TransitAgency, model_LittlepayConfig):
        model_LittlepayConfig.transit_agency = model_TransitAgency
        model_TransitAgency.save()

        assert model_TransitAgency.in_person_enrollment_index_route == routes.IN_PERSON_ENROLLMENT_LITTLEPAY_INDEX

    def test_in_person_enrollment_index_route_switchio(self, model_TransitAgency, model_SwitchioConfig):
        model_SwitchioConfig.transit_agency = model_TransitAgency
        model_TransitAgency.save()

        assert model_TransitAgency.in_person_enrollment_index_route == routes.IN_PERSON_ENROLLMENT_SWITCHIO_INDEX

    def test_in_person_enrollment_index_route_no_config(self, model_TransitAgency):
        with pytest.raises(
            ValueError,
            match=(
                "TransitAgency must have either a LittlepayConfig or SwitchioConfig "
                "in order to show in-person enrollment index."
            ),
        ):
            model_TransitAgency.in_person_enrollment_index_route

    def test_customer_service_group_name(self, model_TransitAgency):
        model_TransitAgency.short_name = "CST"
        assert model_TransitAgency.customer_service_group_name == "CST Customer Service"

    @pytest.mark.usefixtures("model_TransitAgencyGroup")
    def test_group_agencies(self, model_TransitAgency, model_TransitAgency_2):
        assert model_TransitAgency_2 in model_TransitAgency.group_agencies()

    def test_group_agencies__excludes_inactives(
        self, model_TransitAgency_2, model_TransitAgency_inactive, model_TransitAgencyGroup
    ):
        model_TransitAgencyGroup.transit_agencies.add(model_TransitAgency_2, model_TransitAgency_inactive)
        model_TransitAgencyGroup.save()

        assert model_TransitAgency_inactive not in model_TransitAgency_2.group_agencies()

    @pytest.mark.usefixtures("model_TransitAgencyGroup")
    def test_group_agencies__excludes_self(self, model_TransitAgency):
        assert model_TransitAgency not in model_TransitAgency.group_agencies()

    @pytest.mark.usefixtures("model_TransitAgencyGroup")
    def test_group_agencies__returns_agency_in_multiple_groups_once(self, model_TransitAgency, model_TransitAgency_2):
        group2 = TransitAgencyGroup.objects.create(label="group2")
        group2.transit_agencies.add(model_TransitAgency, model_TransitAgency_2)

        assert len(model_TransitAgency.group_agencies()) == 1


@pytest.mark.django_db
def test_TransitAgencyGroup_str(model_TransitAgencyGroup):
    assert str(model_TransitAgencyGroup) == model_TransitAgencyGroup.label
