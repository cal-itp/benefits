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

    @pytest.mark.parametrize(
        "runtime_env,user_type,expected",
        [
            (settings.RUNTIME_ENVS.PROD, "staff", False),
            (settings.RUNTIME_ENVS.PROD, "super", False),
            (settings.RUNTIME_ENVS.DEV, "staff", True),
            (settings.RUNTIME_ENVS.DEV, "super", True),
        ],
    )
    def test_has_add_permission(
        self,
        admin_user_request,
        event_admin_model,
        settings,
        runtime_env,
        user_type,
        expected,
    ):
        settings.RUNTIME_ENVIRONMENT = lambda: runtime_env

        request = admin_user_request(user_type)

        assert event_admin_model.has_add_permission(request) == expected

    @pytest.mark.parametrize(
        "runtime_env,user_type,expected",
        [
            (settings.RUNTIME_ENVS.PROD, "staff", False),
            (settings.RUNTIME_ENVS.PROD, "super", False),
            (settings.RUNTIME_ENVS.TEST, "staff", False),
            (settings.RUNTIME_ENVS.TEST, "super", True),
        ],
    )
    def test_has_change_permission(
        self,
        admin_user_request,
        event_admin_model,
        settings,
        runtime_env,
        user_type,
        expected,
    ):
        settings.RUNTIME_ENVIRONMENT = lambda: runtime_env

        request = admin_user_request(user_type)

        assert event_admin_model.has_change_permission(request) == expected

    @pytest.mark.parametrize(
        "user_type,expected",
        [
            ("staff", True),
            ("super", True),
        ],
    )
    def test_has_view_permission(self, admin_user_request, event_admin_model, user_type, expected):
        request = admin_user_request(user_type)

        assert event_admin_model.has_view_permission(request) == expected


@pytest.mark.django_db
class TestEnrollmentFlowAdmin:

    @pytest.mark.parametrize(
        "user_type,expected",
        [
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
    def test_get_exclude(self, admin_user_request, flow_admin_model, user_type, expected):
        request = admin_user_request(user_type)

        excluded = flow_admin_model.get_exclude(request)

        if expected:
            assert set(excluded) == set(expected)
        else:
            assert excluded is None

    @pytest.mark.parametrize(
        "user_type,expected",
        [
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
    def test_get_readonly_fields(self, admin_user_request, flow_admin_model, user_type, expected):
        request = admin_user_request(user_type)

        readonly = flow_admin_model.get_readonly_fields(request)

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
    def test_has_add_permission(
        self,
        admin_user_request,
        flow_admin_model,
        settings,
        runtime_env,
        user_type,
        expected,
    ):
        settings.RUNTIME_ENVIRONMENT = lambda: runtime_env

        request = admin_user_request(user_type)

        assert flow_admin_model.has_add_permission(request) == expected
