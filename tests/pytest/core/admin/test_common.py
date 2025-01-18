import pytest

from django.contrib import admin

from benefits.core import models
from benefits.core.admin.common import PemDataAdmin


@pytest.fixture
def admin_model():
    return PemDataAdmin(models.PemData, admin.site)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_type,expected",
    [("regular", ["remote_url", "text_secret_name"]), ("staff", ["remote_url", "text_secret_name"]), ("super", None)],
)
def test_exclude_fields(admin_user_request, admin_model, user_type, expected):
    request = admin_user_request(user_type)

    exclude = admin_model.get_exclude(request)

    if expected:
        assert set(exclude) == set(expected)
    else:
        assert exclude is None


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_type,expected",
    [("regular", ["label"]), ("staff", ["label"]), ("super", ())],
)
def test_readonly_fields(admin_user_request, admin_model, user_type, expected):
    request = admin_user_request(user_type)

    readonly = admin_model.get_readonly_fields(request)

    assert set(readonly) == set(expected)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_type,expected",
    [("regular", False), ("super", True)],
)
def test_has_add_permission(
    admin_user_request,
    admin_model,
    user_type,
    expected,
):
    request = admin_user_request(user_type)

    assert admin_model.has_add_permission(request) == expected
