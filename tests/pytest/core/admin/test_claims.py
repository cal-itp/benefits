import pytest

from django.contrib import admin

from benefits.core import models
from benefits.core.admin.claims import ClaimsProviderAdmin


@pytest.fixture
def admin_model():
    return ClaimsProviderAdmin(models.ClaimsProvider, admin.site)


@pytest.mark.parametrize(
    "user_type,expected",
    [("staff", ["client_id_secret_name"]), ("super", None)],
)
@pytest.mark.django_db
def test_get_exclude(admin_model, admin_user_request, user_type, expected):
    request = admin_user_request(user_type)

    exclude = admin_model.get_exclude(request)

    if expected:
        assert set(exclude) == set(expected)
    else:
        assert exclude is None


@pytest.mark.parametrize(
    "user_type,expected",
    [
        ("staff", ["sign_out_button_template", "sign_out_link_template", "client_id_secret_name", "authority", "scheme"]),
        ("super", ()),
    ],
)
@pytest.mark.django_db
def test_get_readonly_fields(admin_model, admin_user_request, user_type, expected):
    request = admin_user_request(user_type)

    readonly = admin_model.get_readonly_fields(request)

    assert set(readonly) == set(expected)
