import pytest

from benefits.admin import pre_login_user


@pytest.mark.django_db
def test_pre_login_user(mocker, model_AdminUser):
    assert model_AdminUser.email == "user@compiler.la"
    assert model_AdminUser.first_name == ""
    assert model_AdminUser.last_name == ""
    assert model_AdminUser.username == ""

    response_from_google = {
        "username": "admin@compiler.la",
        "given_name": "Admin",
        "family_name": "User",
        "email": "admin@compiler.la",
    }

    mocked_request = mocker.Mock()
    mocked_response = mocker.Mock()
    mocked_response.json.return_value = response_from_google
    mocker.patch("benefits.admin.requests.get", return_value=mocked_response)

    pre_login_user(model_AdminUser, mocked_request)

    assert model_AdminUser.email == response_from_google["email"]
    assert model_AdminUser.first_name == response_from_google["given_name"]
    assert model_AdminUser.last_name == response_from_google["family_name"]
    assert model_AdminUser.username == response_from_google["username"]
