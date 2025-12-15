import pytest
from django.contrib import admin
from django.contrib.auth.models import Group

from benefits.core import models
from benefits.core.admin.mixins import StaffPermissionMixin, SuperuserPermissionMixin
from benefits.core.admin.transit import EligibilityApiConfigAdmin, TransitAgencyAdmin


@pytest.mark.django_db
class TestEligibilityApiConfigAdmin:
    @pytest.fixture(autouse=True)
    def init(self):
        self.model_admin = EligibilityApiConfigAdmin(models.EligibilityApiConfig, admin.site)

    def test_permissions_mixin(self):
        assert isinstance(self.model_admin, SuperuserPermissionMixin)


@pytest.mark.django_db
class TestTransitAgencyAdmin:
    @pytest.fixture(autouse=True)
    def init(self):
        self.model_admin = TransitAgencyAdmin(models.TransitAgency, admin.site)

    def test_permissions_mixin(self):
        assert isinstance(self.model_admin, StaffPermissionMixin)

    @pytest.mark.parametrize(
        "user_type,expected",
        [
            (
                "staff",
                ["sso_domain", "customer_service_group"],
            ),
            ("super", ["customer_service_group"]),
        ],
    )
    def test_get_exclude(self, admin_user_request, user_type, expected):
        if expected:
            model_fields = [f.name for f in self.model_admin.model._meta.get_fields()]
            assert all(field in model_fields for field in expected)

        request = admin_user_request(user_type)

        excluded = self.model_admin.get_exclude(request)

        if expected:
            assert set(excluded) == set(expected)
        else:
            assert excluded is None

    @pytest.mark.parametrize(
        "user_type,expected",
        [
            ("staff", ["sso_domain"]),
            ("super", []),
        ],
    )
    def test_get_exclude_modify_agency(self, admin_user_request, user_type, expected, model_TransitAgency):
        obj = model_TransitAgency
        request = admin_user_request(user_type)
        excluded = self.model_admin.get_exclude(request, obj)

        if expected:
            assert set(excluded) == set(expected)
        else:
            assert excluded is None

    def test_save_model_create_agency(self, admin_user_request, model_TransitAgency):
        request = admin_user_request("super")
        obj = model_TransitAgency
        form = None
        change = False  # Simulate creating a new agency
        initial_group_count = Group.objects.count()

        self.model_admin.save_model(request, obj, form, change)

        assert obj.customer_service_group.name == f"{obj.short_name} Customer Service"
        assert Group.objects.count() == initial_group_count + 1

    def test_save_model_modify_agency(self, admin_user_request, model_TransitAgency):
        request = admin_user_request("super")
        model_TransitAgency.customer_service_group = Group.objects.create(name="Existing Customer Service Group")
        obj = model_TransitAgency
        form = None
        change = True  # Simulate modifying an existing agency
        initial_group_count = Group.objects.count()

        self.model_admin.save_model(request, obj, form, change)

        assert obj.customer_service_group.name == "Existing Customer Service Group"
        assert Group.objects.count() == initial_group_count
