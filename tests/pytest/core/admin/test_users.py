import pytest
from django.contrib import admin
from django.contrib.auth.models import Group, User

import benefits.core.admin
from benefits.core.admin.mixins import StaffPermissionMixin
from benefits.core.admin.users import GOOGLE_USER_INFO_URL, GroupAdmin, UserAdmin, pre_login_user


@pytest.mark.django_db
class TestGroupAdmin:
    @pytest.fixture(autouse=True)
    def init(self):
        self.model_admin = GroupAdmin(Group, admin.site)

    def test_permission_mixin(self):
        assert isinstance(self.model_admin, StaffPermissionMixin)

    def test_exclude(self):
        assert "permissions" in self.model_admin.exclude


@pytest.mark.django_db
class TestUserAdmin:
    @pytest.fixture(autouse=True)
    def init(self):
        self.model_admin = UserAdmin(User, admin.site)

    def test_permission_mixin(self):
        assert isinstance(self.model_admin, StaffPermissionMixin)

    # test_get_fieldsets are not parameterized by pytest because of some state
    # leakage in how admin_user_request works across parameterized tests
    # instead just write 2 distinct tests to ensure a clean setup each time

    def test_get_fieldsets__superuser(self, admin_user_request):
        request = admin_user_request("super")

        # call get_fieldsets simulating the "Change" page by passing the current user
        # otherwise the default simulates the "Add" page which doesn't have the Permissions fieldset
        fieldsets = self.model_admin.get_fieldsets(request, obj=request.user)

        permissions_fields = None
        for name, options in fieldsets:
            if name == "Permissions":
                permissions_fields = options["fields"]
                break

        assert permissions_fields is not None
        assert "user_permissions" not in permissions_fields
        assert "is_superuser" in permissions_fields

    def test_get_fieldsets__staffuser(self, admin_user_request):
        request = admin_user_request("staff")

        # call get_fieldsets simulating the "Change" page by passing the current user
        # otherwise the default simulates the "Add" page which doesn't have the Permissions fieldset
        fieldsets = self.model_admin.get_fieldsets(request, obj=request.user)

        permissions_fields = None
        for name, options in fieldsets:
            if name == "Permissions":
                permissions_fields = options["fields"]
                break

        assert permissions_fields is not None
        assert "user_permissions" not in permissions_fields
        assert "is_superuser" not in permissions_fields


@pytest.mark.django_db
def test_admin_registered(client):
    response = client.get("/admin", follow=True)

    assert response.status_code == 200
    assert ("/admin/", 301) in response.redirect_chain
    assert ("/admin/login/?next=/admin/", 302) in response.redirect_chain
    assert response.request["PATH_INFO"] == "/admin/login/"
    assert "google_sso/login.html" in response.template_name


@pytest.mark.django_db
def test_pre_login_user(mocker, model_AdminUser):
    assert model_AdminUser.email == "user@calitp.org"
    assert model_AdminUser.first_name == ""
    assert model_AdminUser.last_name == ""
    assert model_AdminUser.username == ""

    response_from_google = {
        "username": "admin@calitp.org",
        "given_name": "Admin",
        "family_name": "User",
        "email": "admin@calitp.org",
    }

    mocked_request = mocker.Mock()
    mocked_response = mocker.Mock()
    mocked_response.json.return_value = response_from_google
    requests_spy = mocker.patch("benefits.core.admin.users.requests.get", return_value=mocked_response)

    pre_login_user(model_AdminUser, mocked_request)

    requests_spy.assert_called_once()
    assert GOOGLE_USER_INFO_URL in requests_spy.call_args.args
    assert model_AdminUser.email == response_from_google["email"]
    assert model_AdminUser.first_name == response_from_google["given_name"]
    assert model_AdminUser.last_name == response_from_google["family_name"]
    assert model_AdminUser.username == response_from_google["username"]


@pytest.mark.django_db
def test_pre_login_user_no_session_token(mocker, model_AdminUser):
    mocked_request = mocker.Mock()
    mocked_request.session.get.return_value = None
    logger_spy = mocker.spy(benefits.core.admin.users, "logger")

    pre_login_user(model_AdminUser, mocked_request)

    assert model_AdminUser.email == "user@calitp.org"
    assert model_AdminUser.first_name == ""
    assert model_AdminUser.last_name == ""
    assert model_AdminUser.username == ""
    logger_spy.warning.assert_called_once()


@pytest.mark.django_db
def test_pre_login_user_add_staff_to_group(mocker, model_AdminUser, settings):
    mocked_request = mocker.Mock()
    mocked_request.session.get.return_value = None

    settings.GOOGLE_SSO_STAFF_LIST = [model_AdminUser.email]
    pre_login_user(model_AdminUser, mocked_request)

    staff_group = Group.objects.get(name=settings.STAFF_GROUP_NAME)
    assert model_AdminUser.groups.contains(staff_group)


@pytest.mark.django_db
def test_pre_login_user_does_not_add_transit_staff_to_group(mocker, settings):
    mocked_request = mocker.Mock()
    mocked_request.session.get.return_value = None

    settings.GOOGLE_SSO_STAFF_LIST = ["*"]
    settings.GOOGLE_SSO_ALLOWABLE_DOMAINS = ["cst.org"]
    # simulate what `django_google_sso` does for us (sets is_staff to True)
    agency_user = User.objects.create_user(username="agency_user", email="manager@cst.org", is_staff=True)

    pre_login_user(agency_user, mocked_request)

    # assert that a transit agency user does not get added to the Cal-ITP user group
    staff_group = Group.objects.get(name=settings.STAFF_GROUP_NAME)
    assert staff_group.user_set.count() == 0
    assert agency_user.groups.count() == 0
