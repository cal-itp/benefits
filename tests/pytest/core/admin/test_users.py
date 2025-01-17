import pytest
from django.contrib.auth.models import User, Group

import benefits.core.admin
from benefits.core.admin.users import GOOGLE_USER_INFO_URL, is_staff_member, is_staff_or_superuser, pre_login_user


@pytest.mark.django_db
def test_admin_registered(client):
    response = client.get("/admin", follow=True)

    assert response.status_code == 200
    assert ("/admin/", 301) in response.redirect_chain
    assert ("/admin/login/?next=/admin/", 302) in response.redirect_chain
    assert response.request["PATH_INFO"] == "/admin/login/"
    assert "google_sso/login.html" in response.template_name


@pytest.mark.django_db
def test_is_staff_member_regular_user(admin_user, staff_group):
    assert not staff_group.user_set.contains(admin_user)
    assert not is_staff_member(admin_user)


@pytest.mark.django_db
def test_is_staff_member_staff_user(admin_user, staff_group):
    staff_group.user_set.add(admin_user)

    assert staff_group.user_set.contains(admin_user)
    assert is_staff_member(admin_user)


@pytest.mark.django_db
def test_is_staff_member_superuser(admin_user, staff_group):
    admin_user.is_superuser = True

    assert not staff_group.user_set.contains(admin_user)
    assert not is_staff_member(admin_user)


@pytest.mark.django_db
def test_is_staff_or_superuser_regular_user(admin_user, staff_group):
    admin_user.is_superuser = False

    assert not staff_group.user_set.contains(admin_user)
    assert not is_staff_or_superuser(admin_user)


@pytest.mark.django_db
def test_is_staff_or_superuser_staff_member(admin_user, staff_group):
    admin_user.is_superuser = False
    staff_group.user_set.add(admin_user)

    assert is_staff_or_superuser(admin_user)


@pytest.mark.django_db
def test_is_staff_or_superuser_superuser(admin_user):
    admin_user.is_superuser = True

    assert is_staff_or_superuser(admin_user)


@pytest.mark.django_db
def test_pre_login_user(mocker, admin_user):
    admin_user.email == "user@calitp.org"
    admin_user.first_name == ""
    admin_user.last_name == ""
    admin_user.username == ""

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

    pre_login_user(admin_user, mocked_request)

    requests_spy.assert_called_once()
    assert GOOGLE_USER_INFO_URL in requests_spy.call_args.args
    assert admin_user.email == response_from_google["email"]
    assert admin_user.first_name == response_from_google["given_name"]
    assert admin_user.last_name == response_from_google["family_name"]
    assert admin_user.username == response_from_google["username"]


@pytest.mark.django_db
def test_pre_login_user_no_session_token(admin_user, mocker):
    mocked_request = mocker.Mock()
    mocked_request.session.get.return_value = None
    logger_spy = mocker.spy(benefits.core.admin.users, "logger")

    pre_login_user(admin_user, mocked_request)

    logger_spy.warning.assert_called_once()


@pytest.mark.django_db
def test_pre_login_user_add_staff_to_group(mocker, admin_user, settings, staff_group):
    mocked_request = mocker.Mock()
    mocked_request.session.get.return_value = None

    settings.GOOGLE_SSO_STAFF_LIST = [admin_user.email]
    pre_login_user(admin_user, mocked_request)

    assert admin_user.groups.contains(staff_group)


@pytest.mark.django_db
def test_pre_login_user_does_not_add_transit_staff_to_group(mocker, settings, staff_group):
    mocked_request = mocker.Mock()
    mocked_request.session.get.return_value = None

    settings.GOOGLE_SSO_STAFF_LIST = ["*"]
    settings.GOOGLE_SSO_ALLOWABLE_DOMAINS = ["cst.org"]
    # simulate what `django_google_sso` does for us (sets is_staff to True)
    agency_user = User.objects.create_user(username="agency_user", email="manager@cst.org", is_staff=True)

    pre_login_user(agency_user, mocked_request)

    # assert that a transit agency user does not get added to the Cal-ITP user group
    assert staff_group.user_set.count() == 0
    assert agency_user.groups.count() == 0


@pytest.mark.django_db
def test_pre_login_user_add_transit_staff_to_transit_staff_group(mocker, settings, model_TransitAgency):
    mocked_request = mocker.Mock()
    mocked_request.session.get.return_value = None

    transit_agency_staff_group = Group.objects.create(name="CST Staff")
    model_TransitAgency.pk = None
    model_TransitAgency.staff_group = transit_agency_staff_group
    model_TransitAgency.sso_domain = "cst.org"
    model_TransitAgency.save()

    settings.GOOGLE_SSO_STAFF_LIST = ["*"]
    settings.GOOGLE_SSO_ALLOWABLE_DOMAINS = ["cst.org"]

    # simulate what `django_google_sso` does for us (sets is_staff to True)
    agency_user = User.objects.create_user(username="agency_user", email="manager@cst.org", is_staff=True)

    pre_login_user(agency_user, mocked_request)

    # assert that a transit agency user gets added to their TransitAgency's staff group based on SSO domain
    assert agency_user.groups.count() == 1
    assert agency_user.groups.first() == transit_agency_staff_group
