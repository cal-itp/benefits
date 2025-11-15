import pytest
from django.contrib import admin

from benefits.core import models
from benefits.core.admin.transit import TransitAgencyAdmin
from benefits.core.admin.mixins import StaffPermissionMixin


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
                [
                    "eligibility_api_private_key",
                    "eligibility_api_public_key",
                    "sso_domain",
                ],
            ),
            ("super", ()),
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
            (
                "staff",
                ["eligibility_api_id"],
            ),
            ("super", ()),
        ],
    )
    def test_get_readonly_fields(self, admin_user_request, user_type, expected):
        if expected:
            model_fields = [f.name for f in self.model_admin.model._meta.get_fields()]
            assert all(field in model_fields for field in expected)

        request = admin_user_request(user_type)

        readonly = self.model_admin.get_readonly_fields(request)

        assert set(readonly) == set(expected)
