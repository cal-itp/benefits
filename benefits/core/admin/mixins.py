from django.conf import settings
from django.contrib.auth.models import Group


def is_staff_member(user):
    """Determine if a user is a member of the staff group of Benefits.

    The staff group of Benefits is also called the 'Cal-ITP' group (defined in settings.STAFF_GROUP_NAME)
    and it is not to be confused with Django's concept of 'staff' which simply means users that can log in to the admin.
    """

    staff_group = Group.objects.get(name=settings.STAFF_GROUP_NAME)
    return staff_group.user_set.contains(user)


def is_staff_member_or_superuser(user):
    """Determine if a user is a member of the staff group of Benefits or if it is a superuser."""
    # an AnonymousUser can't be a staff member or superuser
    if not user.is_authenticated:
        return False
    return user.is_superuser or is_staff_member(user)


class ProdReadOnlyPermissionMixin:
    """A specific mixin for models that should be read-only in Production.

    - Grants `view` to staff/superusers.
    - In Prod: Blocks `add/change/delete` for all users.
    - In Non-Prod: Grants `add/change/delete` to staff/superusers.
    """

    def _user_can_manage(self, request):
        """Central logic to check if a user has full management permissions for this model."""
        if settings.RUNTIME_ENVIRONMENT() == settings.RUNTIME_ENVS.PROD:
            return False
        return request.user and is_staff_member_or_superuser(request.user)

    def has_add_permission(self, request):
        return self._user_can_manage(request)

    def has_change_permission(self, request, obj=None):
        return self._user_can_manage(request)

    def has_delete_permission(self, request, obj=None):
        return self._user_can_manage(request)

    def has_module_permission(self, request, obj=None):
        # View is always allowed for staff, even in Prod
        return request.user and is_staff_member_or_superuser(request.user)

    def has_view_permission(self, request, obj=None):
        # View is always allowed for staff, even in Prod
        return request.user and is_staff_member_or_superuser(request.user)


class StaffPermissionMixin:
    """Grants full `add/change/delete/view` permissions to users who pass the `is_staff_member_or_superuser` check."""

    def _user_can_manage(self, request):
        """Central logic to check if a user has full management permissions for this model."""
        return request.user and is_staff_member_or_superuser(request.user)

    def has_add_permission(self, request):
        return self._user_can_manage(request)

    def has_change_permission(self, request, obj=None):
        return self._user_can_manage(request)

    def has_delete_permission(self, request, obj=None):
        return self._user_can_manage(request)

    def has_module_permission(self, request):
        return self._user_can_manage(request)

    def has_view_permission(self, request, obj=None):
        return self._user_can_manage(request)


class SuperuserPermissionMixin:
    """Grants `add/change/delete/view` permissions to superusers only."""

    def _user_can_manage(self, request):
        """Central logic to check if a user has full management permissions for this model."""
        return request.user and request.user.is_superuser

    def has_add_permission(self, request):
        return self._user_can_manage(request)

    def has_change_permission(self, request, obj=None):
        return self._user_can_manage(request)

    def has_delete_permission(self, request, obj=None):
        return self._user_can_manage(request)

    def has_module_permission(self, request, obj=None):
        return self._user_can_manage(request)

    def has_view_permission(self, request, obj=None):
        return self._user_can_manage(request)
