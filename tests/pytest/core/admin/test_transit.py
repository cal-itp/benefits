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
                "regular",
                [
                    "customer_service_group",
                    "eligibility_api_private_key",
                    "eligibility_api_public_key",
                    "sso_domain",
                    "staff_group",
                    "transit_processor_client_id",
                    "transit_processor_audience",
                    "transit_processor_client_secret_name",
                ],
            ),
            (
                "staff",
                [
                    "eligibility_api_private_key",
                    "eligibility_api_public_key",
                    "sso_domain",
                    "transit_processor_client_secret_name",
                    "transit_processor_audience",
                    "transit_processor_client_id",
                ],
            ),
            ("super", None),
        ],
    )
    def test_get_exclude(self, admin_request, agency_admin_model, user_type, expected):
        if user_type == "regular":
            request = admin_request(is_superuser=False, is_staff=False)
        elif user_type == "staff":
            request = admin_request(is_superuser=False, is_staff=True)
        elif user_type == "super":
            request = admin_request(is_superuser=True, is_staff=False)

        excluded = agency_admin_model.get_exclude(request)

        if expected:
            assert set(excluded) == set(expected)
        else:
            assert excluded is None

    @pytest.mark.parametrize(
        "user_type,expected",
        [
            (
                "regular",
                [
                    "active",
                    "eligibility_api_id",
                    "eligibility_index_template_override",
                    "index_template_override",
                    "slug",
                    "transit_processor",
                ],
            ),
            (
                "staff",
                [
                    "eligibility_index_template_override",
                    "eligibility_api_id",
                    "index_template_override",
                    "transit_processor",
                ],
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
            (settings.RUNTIME_ENVS.PROD, "regular", False),
            (settings.RUNTIME_ENVS.PROD, "staff", True),
            (settings.RUNTIME_ENVS.PROD, "super", True),
            (settings.RUNTIME_ENVS.DEV, "regular", True),
            (settings.RUNTIME_ENVS.DEV, "staff", True),
            (settings.RUNTIME_ENVS.DEV, "super", True),
        ],
    )
    def test_has_add_permission(self, admin_request, agency_admin_model, settings, runtime_env, user_type, expected):
        settings.RUNTIME_ENVIRONMENT = lambda: runtime_env

        if user_type == "regular":
            request = admin_request(is_superuser=False, is_staff=False)
        elif user_type == "staff":
            request = admin_request(is_superuser=False, is_staff=True)
        elif user_type == "super":
            request = admin_request(is_superuser=True, is_staff=False)

        assert agency_admin_model.has_add_permission(request) == expected


@pytest.mark.django_db
class TestTransitProcessorAdmin:

    @pytest.mark.parametrize(
        "user_type,expected",
        [
            ("regular", ["card_tokenize_url", "card_tokenize_func", "card_tokenize_env"]),
            ("staff", None),
            ("super", None),
        ],
    )
    def test_get_exclude(self, admin_request, processor_admin_model, user_type, expected):
        if user_type == "regular":
            request = admin_request(is_superuser=False, is_staff=False)
        elif user_type == "staff":
            request = admin_request(is_superuser=False, is_staff=True)
        elif user_type == "super":
            request = admin_request(is_superuser=True, is_staff=False)

        excluded = processor_admin_model.get_exclude(request)

        if expected:
            assert set(excluded) == set(expected)

    @pytest.mark.parametrize(
        "user_type,expected",
        [
            ("regular", ["name", "api_base_url", "card_tokenize_env", "card_tokenize_func", "card_tokenize_url"]),
            ("staff", ["card_tokenize_url", "card_tokenize_func", "card_tokenize_env"]),
            ("super", ()),
        ],
    )
    def test_get_readonly_fields(self, admin_request, processor_admin_model, user_type, expected):
        if user_type == "regular":
            request = admin_request(is_superuser=False, is_staff=False)
        elif user_type == "staff":
            request = admin_request(is_superuser=False, is_staff=True)
        elif user_type == "super":
            request = admin_request(is_superuser=True, is_staff=False)

        readonly = processor_admin_model.get_readonly_fields(request)

        assert set(readonly) == set(expected)

    @pytest.mark.parametrize(
        "runtime_env,user_type,expected",
        [
            (settings.RUNTIME_ENVS.PROD, "regular", False),
            (settings.RUNTIME_ENVS.PROD, "staff", False),
            (settings.RUNTIME_ENVS.PROD, "super", True),
            (settings.RUNTIME_ENVS.DEV, "regular", True),
            (settings.RUNTIME_ENVS.DEV, "staff", True),
            (settings.RUNTIME_ENVS.DEV, "super", True),
        ],
    )
    def test_has_add_permission(self, admin_request, processor_admin_model, settings, runtime_env, user_type, expected):
        settings.RUNTIME_ENVIRONMENT = lambda: runtime_env

        if user_type == "regular":
            request = admin_request(is_superuser=False, is_staff=False)
        elif user_type == "staff":
            request = admin_request(is_superuser=False, is_staff=True)
        elif user_type == "super":
            request = admin_request(is_superuser=True, is_staff=False)

        assert processor_admin_model.has_add_permission(request) == expected
