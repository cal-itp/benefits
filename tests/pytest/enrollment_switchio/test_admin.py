import pytest
from django.contrib import admin

from benefits.core.admin.mixins import StaffPermissionMixin
from benefits.enrollment_switchio import models
from benefits.enrollment_switchio.admin import SwitchioConfigAdmin, SwitchioGroupAdmin


@pytest.mark.django_db
class TestLittlepayConfigAdmin:
    @pytest.fixture(autouse=True)
    def init(self):
        self.model_admin = SwitchioConfigAdmin(models.SwitchioConfig, admin.site)

    def test_permissions_mixin(self):
        assert isinstance(self.model_admin, StaffPermissionMixin)


@pytest.mark.django_db
class TestLittlepayGroupAdmin:
    @pytest.fixture(autouse=True)
    def init(self):
        self.model_admin = SwitchioGroupAdmin(models.SwitchioGroup, admin.site)

    def test_permissions_mixin(self):
        assert isinstance(self.model_admin, StaffPermissionMixin)
