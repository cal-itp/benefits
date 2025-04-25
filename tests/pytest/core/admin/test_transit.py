import pytest

from django.conf import settings
from django.contrib import admin

from benefits.core.admin.transit import TransitAgencyAdmin, TransitProcessorAdmin
from benefits.core import models


@pytest.fixture
def agency_admin_model():
    return TransitAgencyAdmin(models.TransitAgency, admin.site)


@pytest.fixture
def processor_admin_model():
    return TransitProcessorAdmin(models.TransitProcessor, admin.site)


@pytest.mark.django_db
class TestTransitAgencyAdmin:

    @pytest.mark.parametrize(
        "user_type,expected",
        [
            (
                "staff",
                [
                    "eligibility_api_private_key",
                    "eligibility_api_public_key",
                    "sso_domain",
                    "littlepay_config",
                    "switchio_config",
                ],
            ),
            ("super", None),
        ],
    )
    def test_get_exclude(self, admin_user_request, agency_admin_model, user_type, expected):
        request = admin_user_request(user_type)

        excluded = agency_admin_model.get_exclude(request)

        if expected:
            assert set(excluded) == set(expected)
        else:
            assert excluded is None

    @pytest.mark.parametrize(
        "user_type,expected",
        [
            (
                "staff",
                ["eligibility_api_id", "transit_processor"],
            ),
            ("super", ()),
        ],
    )
    def test_get_readonly_fields(self, admin_user_request, agency_admin_model, user_type, expected):
        request = admin_user_request(user_type)

        readonly = agency_admin_model.get_readonly_fields(request)

        assert set(readonly) == set(expected)

    @pytest.mark.parametrize(
        "runtime_env,user_type,expected",
        [
            (settings.RUNTIME_ENVS.PROD, "staff", True),
            (settings.RUNTIME_ENVS.PROD, "super", True),
            (settings.RUNTIME_ENVS.DEV, "staff", True),
            (settings.RUNTIME_ENVS.DEV, "super", True),
        ],
    )
    def test_has_add_permission(self, admin_user_request, agency_admin_model, settings, runtime_env, user_type, expected):
        settings.RUNTIME_ENVIRONMENT = lambda: runtime_env

        request = admin_user_request(user_type)

        assert agency_admin_model.has_add_permission(request) == expected


@pytest.mark.django_db
class TestTransitProcessorAdmin:

    @pytest.mark.parametrize(
        "user_type,expected",
        [
            ("staff", ["api_base_url", "card_tokenize_url", "card_tokenize_func", "card_tokenize_env"]),
            ("super", ()),
        ],
    )
    def test_get_exclude(self, admin_user_request, processor_admin_model, user_type, expected):
        request = admin_user_request(user_type)

        excluded = processor_admin_model.get_exclude(request)

        if expected:
            assert set(excluded) == set(expected)

    @pytest.mark.parametrize(
        "runtime_env,user_type,expected",
        [
            (settings.RUNTIME_ENVS.PROD, "staff", False),
            (settings.RUNTIME_ENVS.PROD, "super", True),
            (settings.RUNTIME_ENVS.DEV, "staff", True),
            (settings.RUNTIME_ENVS.DEV, "super", True),
        ],
    )
    def test_has_add_permission(self, admin_user_request, processor_admin_model, settings, runtime_env, user_type, expected):
        settings.RUNTIME_ENVIRONMENT = lambda: runtime_env

        request = admin_user_request(user_type)

        assert processor_admin_model.has_add_permission(request) == expected
