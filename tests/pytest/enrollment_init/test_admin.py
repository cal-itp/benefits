import pytest
from django.contrib import admin

from benefits.core.admin.mixins import StaffPermissionMixin
from benefits.enrollment_init import models
from benefits.enrollment_init.admin import InitConfigAdmin


@pytest.mark.django_db
class TestInitConfigAdmin:
    @pytest.fixture(autouse=True)
    def init(self):
        self.model_admin = InitConfigAdmin(models.InitConfig, admin.site)

    def test_permissions_mixin(self):
        assert isinstance(self.model_admin, StaffPermissionMixin)
