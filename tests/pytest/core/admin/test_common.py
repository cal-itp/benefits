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
def test_exclude_fields(admin_request, admin_model, user_type, expected):
    if user_type == "regular":
        request = admin_request(is_superuser=False, is_staff=False)
    if user_type == "staff":
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
    [("regular", ["label"]), ("staff", ["label"]), ("super", ())],
)
def test_readonly_fields(admin_request, admin_model, user_type, expected):
    if user_type == "regular":
        request = admin_request(is_superuser=False, is_staff=False)
    if user_type == "staff":
        request = admin_request(is_superuser=False, is_staff=True)
    elif user_type == "super":
        request = admin_request(is_superuser=True, is_staff=False)

    readonly = admin_model.get_readonly_fields(request)

    assert set(readonly) == set(expected)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_type,expected",
    [("regular", False), ("super", True)],
)
def test_has_add_permission(
    admin_request,
    admin_model,
    user_type,
    expected,
):
    if user_type == "regular":
        request = admin_request(is_superuser=False, is_staff=False)
    elif user_type == "super":
        request = admin_request(is_superuser=True, is_staff=False)

    assert admin_model.has_add_permission(request) == expected
