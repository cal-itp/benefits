from django.conf import settings

import pytest

from benefits.core.admin.mixins import ProdReadOnlyPermissionMixin, StaffPermissionMixin, SuperuserPermissionMixin


@pytest.mark.django_db
class TestPermissionsMixins:

    @pytest.mark.parametrize(
        "MixinClass,runtime_env,user_type,expected",
        [
            (ProdReadOnlyPermissionMixin, settings.RUNTIME_ENVS.PROD, "staff", False),
            (ProdReadOnlyPermissionMixin, settings.RUNTIME_ENVS.PROD, "super", False),
            (ProdReadOnlyPermissionMixin, settings.RUNTIME_ENVS.TEST, "staff", True),
            (ProdReadOnlyPermissionMixin, settings.RUNTIME_ENVS.TEST, "super", True),
            (StaffPermissionMixin, settings.RUNTIME_ENVS.PROD, "staff", True),
            (StaffPermissionMixin, settings.RUNTIME_ENVS.PROD, "super", True),
            (StaffPermissionMixin, settings.RUNTIME_ENVS.TEST, "staff", True),
            (StaffPermissionMixin, settings.RUNTIME_ENVS.TEST, "super", True),
            (SuperuserPermissionMixin, settings.RUNTIME_ENVS.PROD, "staff", False),
            (SuperuserPermissionMixin, settings.RUNTIME_ENVS.PROD, "super", True),
            (SuperuserPermissionMixin, settings.RUNTIME_ENVS.TEST, "staff", False),
            (SuperuserPermissionMixin, settings.RUNTIME_ENVS.TEST, "super", True),
        ],
    )
    def test_has_add_permission(self, admin_user_request, settings, MixinClass, runtime_env, user_type, expected):
        settings.RUNTIME_ENVIRONMENT = lambda: runtime_env
        request = admin_user_request(user_type)
        mixin = MixinClass()

        assert mixin.has_add_permission(request) == expected

    @pytest.mark.parametrize(
        "MixinClass,runtime_env,user_type,expected",
        [
            (ProdReadOnlyPermissionMixin, settings.RUNTIME_ENVS.PROD, "staff", False),
            (ProdReadOnlyPermissionMixin, settings.RUNTIME_ENVS.PROD, "super", False),
            (ProdReadOnlyPermissionMixin, settings.RUNTIME_ENVS.TEST, "staff", True),
            (ProdReadOnlyPermissionMixin, settings.RUNTIME_ENVS.TEST, "super", True),
            (StaffPermissionMixin, settings.RUNTIME_ENVS.PROD, "staff", True),
            (StaffPermissionMixin, settings.RUNTIME_ENVS.PROD, "super", True),
            (StaffPermissionMixin, settings.RUNTIME_ENVS.TEST, "staff", True),
            (StaffPermissionMixin, settings.RUNTIME_ENVS.TEST, "super", True),
            (SuperuserPermissionMixin, settings.RUNTIME_ENVS.PROD, "staff", False),
            (SuperuserPermissionMixin, settings.RUNTIME_ENVS.PROD, "super", True),
            (SuperuserPermissionMixin, settings.RUNTIME_ENVS.TEST, "staff", False),
            (SuperuserPermissionMixin, settings.RUNTIME_ENVS.TEST, "super", True),
        ],
    )
    def test_has_change_permission(self, admin_user_request, settings, MixinClass, runtime_env, user_type, expected):
        settings.RUNTIME_ENVIRONMENT = lambda: runtime_env
        request = admin_user_request(user_type)
        mixin = MixinClass()

        assert mixin.has_change_permission(request) == expected

    @pytest.mark.parametrize(
        "MixinClass,runtime_env,user_type,expected",
        [
            (ProdReadOnlyPermissionMixin, settings.RUNTIME_ENVS.PROD, "staff", False),
            (ProdReadOnlyPermissionMixin, settings.RUNTIME_ENVS.PROD, "super", False),
            (ProdReadOnlyPermissionMixin, settings.RUNTIME_ENVS.TEST, "staff", True),
            (ProdReadOnlyPermissionMixin, settings.RUNTIME_ENVS.TEST, "super", True),
            (StaffPermissionMixin, settings.RUNTIME_ENVS.PROD, "staff", True),
            (StaffPermissionMixin, settings.RUNTIME_ENVS.PROD, "super", True),
            (StaffPermissionMixin, settings.RUNTIME_ENVS.TEST, "staff", True),
            (StaffPermissionMixin, settings.RUNTIME_ENVS.TEST, "super", True),
            (SuperuserPermissionMixin, settings.RUNTIME_ENVS.PROD, "staff", False),
            (SuperuserPermissionMixin, settings.RUNTIME_ENVS.PROD, "super", True),
            (SuperuserPermissionMixin, settings.RUNTIME_ENVS.TEST, "staff", False),
            (SuperuserPermissionMixin, settings.RUNTIME_ENVS.TEST, "super", True),
        ],
    )
    def test_has_delete_permission(self, admin_user_request, settings, MixinClass, runtime_env, user_type, expected):
        settings.RUNTIME_ENVIRONMENT = lambda: runtime_env
        request = admin_user_request(user_type)
        mixin = MixinClass()

        assert mixin.has_delete_permission(request) == expected

    @pytest.mark.parametrize(
        "MixinClass,runtime_env,user_type,expected",
        [
            (ProdReadOnlyPermissionMixin, settings.RUNTIME_ENVS.PROD, "staff", True),
            (ProdReadOnlyPermissionMixin, settings.RUNTIME_ENVS.PROD, "super", True),
            (ProdReadOnlyPermissionMixin, settings.RUNTIME_ENVS.TEST, "staff", True),
            (ProdReadOnlyPermissionMixin, settings.RUNTIME_ENVS.TEST, "super", True),
            (StaffPermissionMixin, settings.RUNTIME_ENVS.PROD, "staff", True),
            (StaffPermissionMixin, settings.RUNTIME_ENVS.PROD, "super", True),
            (StaffPermissionMixin, settings.RUNTIME_ENVS.TEST, "staff", True),
            (StaffPermissionMixin, settings.RUNTIME_ENVS.TEST, "super", True),
            (SuperuserPermissionMixin, settings.RUNTIME_ENVS.PROD, "staff", False),
            (SuperuserPermissionMixin, settings.RUNTIME_ENVS.PROD, "super", True),
            (SuperuserPermissionMixin, settings.RUNTIME_ENVS.TEST, "staff", False),
            (SuperuserPermissionMixin, settings.RUNTIME_ENVS.TEST, "super", True),
        ],
    )
    def test_has_view_permission(self, admin_user_request, settings, MixinClass, runtime_env, user_type, expected):
        settings.RUNTIME_ENVIRONMENT = lambda: runtime_env
        request = admin_user_request(user_type)
        mixin = MixinClass()

        assert mixin.has_view_permission(request) == expected
