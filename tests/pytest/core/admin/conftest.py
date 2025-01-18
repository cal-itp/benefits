import pytest

from django.contrib.auth.models import Group


@pytest.fixture
def admin_user_request(admin_user, rf, staff_group):
    def _admin_user_request(user_type="regular"):
        request = rf.get("/")
        request.user = admin_user

        if user_type == "regular":
            admin_user.is_superuser = False
            admin_user.is_staff = False
        elif user_type == "staff":
            admin_user.is_superuser = False
            admin_user.is_staff = True
            staff_group.user_set.add(admin_user)
        elif user_type == "super":
            admin_user.is_superuser = True
            admin_user.is_staff = False

        return request

    return _admin_user_request


@pytest.fixture
def staff_group(settings):
    return Group.objects.get(name=settings.STAFF_GROUP_NAME)
