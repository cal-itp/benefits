import pytest

from django.contrib import admin

from benefits.core import models
from benefits.core.admin.common import PemDataAdmin
from benefits.core.admin.mixins import SuperuserPermissionMixin


@pytest.mark.django_db
class TestPemDataAdmin:
    @pytest.fixture(autouse=True)
    def init(self):
        self.model_admin = PemDataAdmin(models.PemData, admin.site)

    def test_permissions_mixin(self):
        assert isinstance(self.model_admin, SuperuserPermissionMixin)
