import pytest
from django.conf import settings
from django.contrib import admin

from benefits.core import models
from benefits.core.admin.transit import EligibilityApiConfigAdmin, TransitAgencyAdmin


@pytest.mark.django_db
class TestEligibilityApiConfigAdmin:
    @pytest.fixture(autouse=True)
    def init(self):
        self.model = EligibilityApiConfigAdmin(models.EligibilityApiConfig, admin.site)

    @pytest.mark.parametrize("user_type,expected", [("staff", False), ("super", True)])
    def test_has_add_permissions(self, admin_user_request, user_type, expected):
        request = admin_user_request(user_type)

        add_permissions = self.model.has_add_permission(request)
        assert add_permissions == expected

    @pytest.mark.parametrize("user_type,expected", [("staff", False), ("super", True)])
    def test_has_view_permissions(self, admin_user_request, user_type, expected):
        request = admin_user_request(user_type)

        add_permissions = self.model.has_view_permission(request)
        assert add_permissions == expected


@pytest.mark.django_db
class TestTransitAgencyAdmin:
    @pytest.fixture(autouse=True)
    def init(self):
        self.model = TransitAgencyAdmin(models.TransitAgency, admin.site)

    @pytest.mark.parametrize(
        "user_type,expected",
        [
            (
                "staff",
                [
                    "sso_domain",
                ],
            ),
            ("super", ()),
        ],
    )
    def test_get_exclude(self, admin_user_request, user_type, expected):
        if expected:
            model_fields = [f.name for f in self.model.model._meta.get_fields()]
            assert all(field in model_fields for field in expected)

        request = admin_user_request(user_type)

        excluded = self.model.get_exclude(request)

        if expected:
            assert set(excluded) == set(expected)
        else:
            assert excluded is None

    @pytest.mark.parametrize(
        "runtime_env,user_type,expected",
        [
            (settings.RUNTIME_ENVS.PROD, "staff", True),
            (settings.RUNTIME_ENVS.PROD, "super", True),
            (settings.RUNTIME_ENVS.DEV, "staff", True),
            (settings.RUNTIME_ENVS.DEV, "super", True),
        ],
    )
    def test_has_add_permission(self, admin_user_request, settings, runtime_env, user_type, expected):
        settings.RUNTIME_ENVIRONMENT = lambda: runtime_env

        request = admin_user_request(user_type)

        assert self.model.has_add_permission(request) == expected
