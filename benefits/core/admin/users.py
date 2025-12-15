import logging

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin, UserAdmin as BaseUserAdmin

import requests

from benefits.core.admin.mixins import StaffPermissionMixin


logger = logging.getLogger(__name__)


GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


# We unregister and re-register both User and Group admins to hide
# the database-level "permissions" fields, making our ModelAdmin
# mixins the single source of truth.
#
# For GroupAdmin, we can just use `exclude` because its default form
# is simple and doesn't use `fieldsets`.
#
# For UserAdmin, we must override `get_fieldsets()` because:
# 1. The default UserAdmin uses `fieldsets`.
# 2. `fieldsets` takes precedence over `exclude`.
admin.site.unregister(Group)
admin.site.unregister(User)


@admin.register(Group)
class GroupAdmin(StaffPermissionMixin, BaseGroupAdmin):
    # This will remove the "Permissions" multi-select box
    # from the Group change page.
    exclude = ("permissions",)


@admin.register(User)
class UserAdmin(StaffPermissionMixin, BaseUserAdmin):
    def get_fieldsets(self, request, obj=None):
        # get the default fieldsets
        # ensures we get any new fields from future Django versions
        fieldsets = super().get_fieldsets(request, obj)
        # Build a set of fields to remove from the "Permissions" section
        fields_to_remove = set()
        fields_to_remove.add("user_permissions")
        if not request.user.is_superuser:
            fields_to_remove.add("is_superuser")
        # create a new list of fieldsets to return
        new_fieldsets = []
        for name, options in fieldsets:
            # find the 'Permissions' fieldset
            if name == "Permissions":
                # copy the fields, but filter out 'user_permissions'
                new_fields = tuple(f for f in options.get("fields", ()) if f not in fields_to_remove)
                options["fields"] = new_fields
            # append the (potentially modified) options for this fieldset
            new_fieldsets.append((name, options))

        return new_fieldsets


def add_google_sso_userinfo(user, request):
    token = request.session.get("google_sso_access_token")
    if token:
        headers = {
            "Authorization": f"Bearer {token}",
        }

        # Request Google user info to get name and email
        response = requests.get(GOOGLE_USER_INFO_URL, headers=headers, timeout=settings.REQUESTS_TIMEOUT)
        user_data = response.json()
        logger.debug(f"Updating user data from Google for user with email: {user_data['email']}")

        user.first_name = user_data["given_name"]
        user.last_name = user_data["family_name"]
        user.username = user_data["email"]
        user.email = user_data["email"]
        user.save()
    else:
        logger.warning("google_sso_access_token not found in session.")


def add_staff_user_to_group(user, request):
    if user.email in settings.GOOGLE_SSO_STAFF_LIST:
        staff_group = Group.objects.get(name=settings.STAFF_GROUP_NAME)
        staff_group.user_set.add(user)


def pre_login_user(user, request):
    logger.debug(f"Running pre-login callback for user: {user.username}")
    add_google_sso_userinfo(user, request)
    add_staff_user_to_group(user, request)
