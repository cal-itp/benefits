import pytest

from django.contrib import admin
from django.conf import settings

from benefits.core import models
from benefits.core.admin.enrollment import EnrollmentEventAdmin, SortableEnrollmentFlowAdmin


@pytest.fixture
def event_admin_model():
    return EnrollmentEventAdmin(models.EnrollmentEvent, admin.site)


@pytest.fixture
def flow_admin_model():
    return SortableEnrollmentFlowAdmin(models.EnrollmentFlow, admin.site)


@pytest.mark.django_db
class TestEnrollmentEventAdmin:

    def test_get_readonly_fields(self, admin_request, event_admin_model):
        request = admin_request(is_superuser=False, is_staff=False)
        assert event_admin_model.get_readonly_fields(request) == ["id"]

    @pytest.mark.parametrize(
        "runtime_env,user_type,expected",
        [
            (settings.RUNTIME_ENVS.PROD, "regular", False),
            (settings.RUNTIME_ENVS.PROD, "staff", False),
            (settings.RUNTIME_ENVS.PROD, "super", False),
            (settings.RUNTIME_ENVS.DEV, "regular", False),
            (settings.RUNTIME_ENVS.DEV, "staff", True),
            (settings.RUNTIME_ENVS.DEV, "super", True),
        ],
    )
    def test_has_add_permission(
        self,
        admin_request,
        event_admin_model,
        settings,
        runtime_env,
        user_type,
        expected,
    ):
        settings.RUNTIME_ENVIRONMENT = lambda: runtime_env

        if user_type == "regular":
            request = admin_request(is_superuser=False, is_staff=False)
        elif user_type == "staff":
            request = admin_request(is_superuser=False, is_staff=True)
        elif user_type == "super":
            request = admin_request(is_superuser=True, is_staff=False)

        assert event_admin_model.has_add_permission(request) == expected

    @pytest.mark.parametrize(
        "runtime_env,user_type,expected",
        [
            (settings.RUNTIME_ENVS.PROD, "regular", False),
            (settings.RUNTIME_ENVS.PROD, "staff", False),
            (settings.RUNTIME_ENVS.PROD, "super", False),
            (settings.RUNTIME_ENVS.TEST, "regular", False),
            (settings.RUNTIME_ENVS.TEST, "staff", False),
            (settings.RUNTIME_ENVS.TEST, "super", True),
        ],
    )
    def test_has_change_permission(
        self,
        admin_request,
        event_admin_model,
        settings,
        runtime_env,
        user_type,
        expected,
    ):
        settings.RUNTIME_ENVIRONMENT = lambda: runtime_env

        if user_type == "regular":
            request = admin_request(is_superuser=False, is_staff=False)
        elif user_type == "staff":
            request = admin_request(is_superuser=False, is_staff=True)
        elif user_type == "super":
            request = admin_request(is_superuser=True, is_staff=False)

        assert event_admin_model.has_change_permission(request) == expected

    @pytest.mark.parametrize(
        "user_type,expected",
        [
            ("regular", False),
            ("staff", True),
            ("super", True),
        ],
    )
    def test_has_view_permission(self, admin_request, event_admin_model, user_type, expected):
        if user_type == "regular":
            request = admin_request(is_superuser=False, is_staff=False)
        elif user_type == "staff":
            request = admin_request(is_superuser=False, is_staff=True)
        elif user_type == "super":
            request = admin_request(is_superuser=True, is_staff=False)

        assert event_admin_model.has_view_permission(request) == expected


@pytest.mark.django_db
class TestEnrollmentFlowAdmin:

    @pytest.mark.parametrize(
        "user_type,expected",
        [
            (
                "regular",
                [
                    "claims_scope",
                    "claims_eligibility_claim",
                    "claims_scheme_override",
                    "eligibility_api_url",
                    "eligibility_form_class",
                    "eligibility_api_auth_header",
                    "eligibility_api_auth_key_secret_name",
                    "eligibility_api_public_key",
                    "eligibility_api_jwe_cek_enc",
                    "eligibility_api_jwe_encryption_alg",
                    "eligibility_api_jws_signing_alg",
                ],
            ),
            (
                "staff",
                [
                    "eligibility_api_auth_header",
                    "eligibility_api_auth_key_secret_name",
                    "eligibility_api_public_key",
                    "eligibility_api_jwe_cek_enc",
                    "eligibility_api_jwe_encryption_alg",
                    "eligibility_api_jws_signing_alg",
                ],
            ),
            ("super", None),
        ],
    )
    def test_get_exclude(self, admin_request, flow_admin_model, user_type, expected):
        if user_type == "regular":
            request = admin_request(is_superuser=False, is_staff=False)
        if user_type == "staff":
            request = admin_request(is_superuser=False, is_staff=True)
        elif user_type == "super":
            request = admin_request(is_superuser=True, is_staff=False)

        excluded = flow_admin_model.get_exclude(request)

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
                    "system_name",
                    "transit_agency",
                    "supported_enrollment_methods",
                    "claims_provider",
                    "supports_expiration",
                    "eligibility_api_url",
                    "eligibility_form_class",
                    "selection_label_template_override",
                    "eligibility_start_template_override",
                    "eligibility_unverified_template_override",
                    "help_template",
                    "enrollment_index_template_override",
                    "reenrollment_error_template",
                    "enrollment_success_template_override",
                ],
            ),
            (
                "staff",
                [
                    "eligibility_api_url",
                    "eligibility_form_class",
                    "eligibility_start_template_override",
                    "eligibility_unverified_template_override",
                    "selection_label_template_override",
                    "reenrollment_error_template",
                    "help_template",
                    "enrollment_index_template_override",
                    "enrollment_success_template_override",
                ],
            ),
            ("super", ()),
        ],
    )
    def test_get_readonly_fields(self, admin_request, flow_admin_model, user_type, expected):
        if user_type == "regular":
            request = admin_request(is_superuser=False, is_staff=False)
        if user_type == "staff":
            request = admin_request(is_superuser=False, is_staff=True)
        elif user_type == "super":
            request = admin_request(is_superuser=True, is_staff=False)

        readonly = flow_admin_model.get_readonly_fields(request)

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
    def test_has_add_permission(
        self,
        admin_request,
        flow_admin_model,
        settings,
        runtime_env,
        user_type,
        expected,
    ):
        settings.RUNTIME_ENVIRONMENT = lambda: runtime_env

        if user_type == "regular":
            request = admin_request(is_superuser=False, is_staff=False)
        elif user_type == "staff":
            request = admin_request(is_superuser=False, is_staff=True)
        else:
            request = admin_request(is_superuser=True, is_staff=False)

        assert flow_admin_model.has_add_permission(request) == expected
