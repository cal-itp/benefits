import pytest

from django.contrib.auth.models import Group


@pytest.fixture
def admin_request(admin_user, rf, staff_group):
    def _admin_request(is_superuser=False, is_staff=False):
        request = rf.get("/")
        request.user = admin_user
        admin_user.is_superuser = is_superuser
        admin_user.is_staff = is_staff
        if is_staff:
            staff_group.user_set.add(admin_user)
        return request

    return _admin_request


@pytest.fixture
def staff_group(settings):
    return Group.objects.get(name=settings.STAFF_GROUP_NAME)
