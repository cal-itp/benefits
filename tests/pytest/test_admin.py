import pytest

from benefits.admin import pre_login_user
from unittest.mock import patch
from requests import Session


@pytest.mark.django_db
@patch.object(Session, "get")
def test_pre_login_user(mock_token_get, model_AdminUser):
    assert model_AdminUser.email == "user@compiler.la"
    assert model_AdminUser.first_name == ""
    assert model_AdminUser.last_name == ""
    assert model_AdminUser.username == ""

    with patch("benefits.admin.requests.get") as mock_response_get:
        mock_token_get.return_value = "TOKEN"
        response_object = {
            "username": "admin@compiler.la",
            "given_name": "Admin",
            "family_name": "User",
            "email": "admin@compiler.la",
        }
        mock_response_get.json.return_value = response_object

        pre_login_user(model_AdminUser, mock_token_get)

        assert model_AdminUser.email == response_object["email"]
        assert model_AdminUser.first_name == response_object["first_name"]
        assert model_AdminUser.last_name == response_object["family_name"]
        assert model_AdminUser.username == response_object["user_name"]
