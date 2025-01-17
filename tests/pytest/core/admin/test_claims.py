import pytest

from django.contrib import admin

from benefits.core import models
from benefits.core.admin.claims import ClaimsProviderAdmin


@pytest.fixture
def admin_model():
    return ClaimsProviderAdmin(models.ClaimsProvider, admin.site)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_type,expected",
    [("regular", ["authority", "scheme", "client_id_secret_name"]), ("staff", ["client_id_secret_name"]), ("super", None)],
)
def test_get_exclude(admin_model, admin_request, user_type, expected):
    if user_type == "regular":
        request = admin_request(is_superuser=False, is_staff=False)
    elif user_type == "staff":
        request = admin_request(is_superuser=False, is_staff=True)
    elif user_type == "super":
        request = admin_request(is_superuser=True, is_staff=False)

    exclude = admin_model.get_exclude(request)

    if expected:
        assert set(exclude) == set(expected)
    else:
        assert exclude is None


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_type,expected",
    [
        (
            "regular",
            [
                "client_name",
                "sign_out_button_template",
                "sign_out_link_template",
                "client_id_secret_name",
                "authority",
                "scheme",
            ],
        ),
        ("staff", ["sign_out_button_template", "sign_out_link_template", "client_id_secret_name", "authority", "scheme"]),
        ("super", ()),
    ],
)
def test_get_readonly_fields(admin_model, admin_request, user_type, expected):
    if user_type == "regular":
        request = admin_request(is_superuser=False, is_staff=False)
    elif user_type == "staff":
        request = admin_request(is_superuser=False, is_staff=True)
    elif user_type == "super":
        request = admin_request(is_superuser=True, is_staff=False)

    readonly = admin_model.get_readonly_fields(request)

    assert set(readonly) == set(expected)
