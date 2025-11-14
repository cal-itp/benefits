from django.conf import settings
from django.contrib.auth.models import Group

import pytest

from benefits.core.admin.mixins import (
    ProdReadOnlyPermissionMixin,
    StaffPermissionMixin,
    SuperuserPermissionMixin,
    is_staff_member,
    is_staff_member_or_superuser,
)


@pytest.mark.django_db
def test_is_staff_member_regular_user(model_AdminUser, settings):
    staff_group = Group.objects.get(name=settings.STAFF_GROUP_NAME)
    assert not staff_group.user_set.contains(model_AdminUser)
    assert not is_staff_member(model_AdminUser)


@pytest.mark.django_db
def test_is_staff_member_staff_user(model_AdminUser, settings):
    staff_group = Group.objects.get(name=settings.STAFF_GROUP_NAME)
    staff_group.user_set.add(model_AdminUser)
    assert staff_group.user_set.contains(model_AdminUser)
    assert is_staff_member(model_AdminUser)


@pytest.mark.django_db
def test_is_staff_member_superuser(model_AdminUser, settings):
    model_AdminUser.is_superuser = True
    model_AdminUser.save()
    staff_group = Group.objects.get(name=settings.STAFF_GROUP_NAME)
    assert not staff_group.user_set.contains(model_AdminUser)
    assert not is_staff_member(model_AdminUser)


@pytest.mark.django_db
def test_is_staff_member_or_superuser_regular_user(model_AdminUser, settings):
    assert not model_AdminUser.is_superuser

    staff_group = Group.objects.get(name=settings.STAFF_GROUP_NAME)

    assert not staff_group.user_set.contains(model_AdminUser)
    assert not is_staff_member_or_superuser(model_AdminUser)


@pytest.mark.django_db
def test_is_staff_member_or_superuser_staff_member(model_AdminUser, settings):
    staff_group = Group.objects.get(name=settings.STAFF_GROUP_NAME)
    staff_group.user_set.add(model_AdminUser)

    assert not model_AdminUser.is_superuser
    assert is_staff_member_or_superuser(model_AdminUser)


@pytest.mark.django_db
def test_is_staff_member_or_superuser_superuser(model_AdminUser):
    model_AdminUser.is_superuser = True
    model_AdminUser.save()

    assert is_staff_member_or_superuser(model_AdminUser)


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
