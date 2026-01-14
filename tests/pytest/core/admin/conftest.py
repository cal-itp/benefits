import pytest
from django.contrib.auth.models import Group, User


@pytest.fixture
def model_AdminUser():
    return User.objects.create(email="user@calitp.org", first_name="", last_name="", username="")


@pytest.fixture
def staff_group(settings):
    return Group.objects.get(name=settings.STAFF_GROUP_NAME)


@pytest.fixture
def admin_user_request(model_AdminUser, rf, staff_group):
    def _admin_user_request(user_type="staff"):
        request = rf.get("/")
        request.user = model_AdminUser

        model_AdminUser.is_staff = True  # a user can log in if and only if this is True

        if user_type == "staff":
            model_AdminUser.is_superuser = False
            staff_group.user_set.add(model_AdminUser)
        elif user_type == "super":
            model_AdminUser.is_superuser = True

        return request

    return _admin_user_request
