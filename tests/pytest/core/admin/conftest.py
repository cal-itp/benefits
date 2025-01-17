import pytest
from django.contrib.auth.models import User, Group


@pytest.fixture
def model_AdminUser():
    return User.objects.create(email="user@calitp.org", first_name="", last_name="", username="")


@pytest.fixture
def staff_group(settings):
    return Group.objects.get(name=settings.STAFF_GROUP_NAME)


@pytest.fixture
def admin_request(model_AdminUser, rf, staff_group):
    def _admin_request(is_superuser=False, is_staff_member=False):
        request = rf.get("/")
        request.user = model_AdminUser
        model_AdminUser.is_superuser = is_superuser
        model_AdminUser.is_staff = True  # a user can log in if and only if this is True
        if is_staff_member:
            staff_group.user_set.add(model_AdminUser)
        return request

    return _admin_request
