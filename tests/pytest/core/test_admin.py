import pytest
from django.contrib.auth.models import User
import benefits.core.admin
from benefits.core.admin import GOOGLE_USER_INFO_URL, pre_login_user


@pytest.fixture
def model_AdminUser():
    return User.objects.create(email="user@calitp.org", first_name="", last_name="", username="")


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
    requests_spy = mocker.patch("benefits.core.admin.requests.get", return_value=mocked_response)

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
    logger_spy = mocker.spy(benefits.core.admin, "logger")

    pre_login_user(model_AdminUser, mocked_request)

    assert model_AdminUser.email == "user@calitp.org"
    assert model_AdminUser.first_name == ""
    assert model_AdminUser.last_name == ""
    assert model_AdminUser.username == ""
    logger_spy.warning.assert_called_once()
