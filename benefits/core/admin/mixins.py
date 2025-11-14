from django.conf import settings

from .users import is_staff_member_or_superuser


class ProdReadOnlyPermissionMixin:
    """
    A specific mixin for models that should be read-only in Production.

    - Grants `view` to staff/superusers.
    - In Prod: Blocks `add/change/delete` for all users.
    - In Non-Prod: Grants `add/change/delete` to staff/superusers.
    """

    def _user_can_manage(self, request):
        """
        Central logic to check if a user has full management permissions for this model.
        """
        if settings.RUNTIME_ENVIRONMENT() == settings.RUNTIME_ENVS.PROD:
            return False
        return request.user and is_staff_member_or_superuser(request.user)

    def has_add_permission(self, request):
        return self._user_can_manage(request)

    def has_change_permission(self, request, obj=None):
        return self._user_can_manage(request)

    def has_delete_permission(self, request, obj=None):
        return self._user_can_manage(request)

    def has_view_permission(self, request, obj=None):
        # View is always allowed for staff, even in Prod
        return request.user and is_staff_member_or_superuser(request.user)


class StaffPermissionMixin:
    """
    Grants full `add/change/delete/view` permissions to users who pass the `is_staff_member_or_superuser` check.
    """

    def _user_can_manage(self, request):
        """
        Central logic to check if a user has full management permissions for this model.
        """
        return request.user and is_staff_member_or_superuser(request.user)

    def has_add_permission(self, request):
        return self._user_can_manage(request)

    def has_change_permission(self, request, obj=None):
        return self._user_can_manage(request)

    def has_delete_permission(self, request, obj=None):
        return self._user_can_manage(request)

    def has_view_permission(self, request, obj=None):
        return self._user_can_manage(request)


class SuperuserPermissionMixin:
    """
    Grants `add/change/delete/view` permissions to superusers only.
    """

    def _user_can_manage(self, request):
        """
        Central logic to check if a user has full management permissions for this model.
        """
        return request.user and request.user.is_superuser

    def has_add_permission(self, request):
        return self._user_can_manage(request)

    def has_change_permission(self, request, obj=None):
        return self._user_can_manage(request)

    def has_delete_permission(self, request, obj=None):
        return self._user_can_manage(request)

    def has_view_permission(self, request, obj=None):
        return self._user_can_manage(request)
