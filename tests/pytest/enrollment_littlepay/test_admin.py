import pytest

from django.contrib import admin

from benefits.core.admin.mixins import StaffPermissionMixin
from benefits.enrollment_littlepay import models
from benefits.enrollment_littlepay.admin import LittlepayConfigAdmin, LittlepayGroupAdmin


@pytest.mark.django_db
class TestLittlepayConfigAdmin:
    @pytest.fixture(autouse=True)
    def init(self):
        self.model_admin = LittlepayConfigAdmin(models.LittlepayConfig, admin.site)

    def test_permissions_mixin(self):
        assert isinstance(self.model_admin, StaffPermissionMixin)


@pytest.mark.django_db
class TestLittlepayGroupAdmin:
    @pytest.fixture(autouse=True)
    def init(self):
        self.model_admin = LittlepayGroupAdmin(models.LittlepayGroup, admin.site)

    def test_permissions_mixin(self):
        assert isinstance(self.model_admin, StaffPermissionMixin)
