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
    [("staff", False), ("super", True)],
)
def test_has_view_permission(
    admin_user_request,
    admin_model,
    user_type,
    expected,
):
    request = admin_user_request(user_type)

    assert admin_model.has_view_permission(request) == expected


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_type,expected",
    [("staff", False), ("super", True)],
)
def test_has_add_permission(
    admin_user_request,
    admin_model,
    user_type,
    expected,
):
    request = admin_user_request(user_type)

    assert admin_model.has_add_permission(request) == expected
