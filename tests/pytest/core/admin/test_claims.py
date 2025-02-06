import pytest

from django.conf import settings
from django.contrib import admin

from benefits.core import models
from benefits.core.admin.claims import ClaimsProviderAdmin


@pytest.fixture
def admin_model():
    return ClaimsProviderAdmin(models.ClaimsProvider, admin.site)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_type,expected",
    [("staff", ["client_id_secret_name"]), ("super", None)],
)
def test_get_exclude(admin_model, admin_user_request, user_type, expected):
    request = admin_user_request(user_type)

    exclude = admin_model.get_exclude(request)

    if expected:
        assert set(exclude) == set(expected)
    else:
        assert exclude is None


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_type,expected",
    [
        ("staff", ["sign_out_button_template", "sign_out_link_template", "authority", "scheme"]),
        ("super", ()),
    ],
)
def test_get_readonly_fields(admin_model, admin_user_request, user_type, expected):
    request = admin_user_request(user_type)

    readonly = admin_model.get_readonly_fields(request)

    assert set(readonly) == set(expected)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "runtime_env,user_type,expected",
    [
        (settings.RUNTIME_ENVS.PROD, "staff", True),
        (settings.RUNTIME_ENVS.PROD, "super", True),
        (settings.RUNTIME_ENVS.DEV, "staff", True),
        (settings.RUNTIME_ENVS.DEV, "super", True),
    ],
)
def test_has_add_permission(admin_model, admin_user_request, settings, runtime_env, user_type, expected):
    settings.RUNTIME_ENVIRONMENT = lambda: runtime_env

    request = admin_user_request(user_type)

    assert admin_model.has_add_permission(request) == expected
