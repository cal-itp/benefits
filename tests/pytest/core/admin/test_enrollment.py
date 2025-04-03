import pytest

from django.contrib import admin
from django.conf import settings
from django.forms import forms

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
                    "selection_label_template_override",
                    "reenrollment_error_template",
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

    def test_EnrollmentFlowForm_staff_member_no_transit_agency(self, admin_user_request, flow_admin_model):
        request = admin_user_request()

        # get the Form class that's used in the admin add view as the user would see it
        form_class = flow_admin_model.get_form(request)

        request.POST = dict(
            system_name="senior",
            supported_enrollment_methods=[models.EnrollmentMethods.DIGITAL, models.EnrollmentMethods.IN_PERSON],
        )

        form = form_class(request.POST)
        assert not form.errors
        assert form.is_valid()

    @pytest.mark.parametrize("active", [True, False])
    def test_EnrollmentFlowForm_staff_member_with_transit_agency(
        self, admin_user_request, flow_admin_model, model_TransitAgency, active
    ):
        model_TransitAgency.active = active
        model_TransitAgency.slug = "mst"  # use value that will map to existing templates
        model_TransitAgency.save()

        request = admin_user_request()

        # get the Form class that's used in the admin add view as the user would see it
        form_class = flow_admin_model.get_form(request)

        request.POST = dict(
            system_name="senior",  # use value that will map to existing templates
            supported_enrollment_methods=[models.EnrollmentMethods.DIGITAL, models.EnrollmentMethods.IN_PERSON],
            transit_agency=model_TransitAgency.id,
        )

        form = form_class(request.POST)

        errors = form.errors
        assert len(errors) == 1

        error = list(errors.values())[0][0]
        assert (
            error
            == "Must configure either claims verification or Eligibility API verification before adding to a transit agency."
        )
        assert not form.is_valid()

    def test_EnrollmentFlowForm_clean_eligibility_api_verification(
        self,
        admin_user_request,
        flow_admin_model,
        model_TransitAgency,
    ):
        model_TransitAgency.slug = "cst"  # use value that will map to existing templates
        model_TransitAgency.save()

        request = admin_user_request("super")

        # fill out the form without a transit agency
        request.POST = dict(
            system_name="senior",  # use value that will map to existing templates
            supported_enrollment_methods=[models.EnrollmentMethods.DIGITAL, models.EnrollmentMethods.IN_PERSON],
            eligibility_api_url="http://server:8000/verify",
            eligibility_form_class="benefits.eligibility.forms.CSTAgencyCard",
            eligibility_api_auth_header="",
            eligibility_api_auth_key_secret_name="",
            eligibility_api_jwe_cek_enc="",
            eligibility_api_jwe_encryption_alg="",
            eligibility_api_jws_signing_alg="",
            eligibility_api_public_key=None,
        )

        form_class = flow_admin_model.get_form(request)

        form = form_class(request.POST)

        # clean is OK
        assert not form.errors
        assert form.is_valid()

        # reassign agency
        request.POST.update(dict(transit_agency=model_TransitAgency.id))

        form = form_class(request.POST)

        assert not form.is_valid()
        error_dict = form.errors
        assert "eligibility_api_auth_header" in error_dict
        assert "eligibility_api_auth_key_secret_name" in error_dict
        assert "eligibility_api_jwe_cek_enc" in error_dict
        assert "eligibility_api_jwe_encryption_alg" in error_dict
        assert "eligibility_api_jws_signing_alg" in error_dict
        assert "eligibility_api_public_key" in error_dict

    def test_EnrollmentFlowForm_clean_supports_expiration_superuser(
        self,
        admin_user_request,
        flow_admin_model,
        model_TransitAgency,
        model_IdentityGatewayConfig,
        model_ClaimsVerificationRequest,
    ):
        model_TransitAgency.slug = "cst"  # use value that will map to existing templates
        model_TransitAgency.save()

        request = admin_user_request(user_type="super")

        request.POST = dict(
            system_name="senior",  # use value that will map to existing templates
            supported_enrollment_methods=[models.EnrollmentMethods.DIGITAL, models.EnrollmentMethods.IN_PERSON],
            transit_agency=model_TransitAgency.id,
            supports_expiration=True,
            expiration_days=365,
            expiration_reenrollment_days=14,
        )

        # fake a valid claims configuration
        request.POST.update(
            dict(
                oauth_config=model_IdentityGatewayConfig.id,
                claims_request=model_ClaimsVerificationRequest.id,
            )
        )

        # but an invalid reenrollment error template
        request.POST.update(dict(reenrollment_error_template="does/not/exist.html"))

        form_class = flow_admin_model.get_form(request)
        form = form_class(request.POST)

        # assert there is a template error
        assert not form.is_valid()
        non_field_errors = form.errors[forms.NON_FIELD_ERRORS]
        assert len(non_field_errors) == 1
        assert "Template not found" in non_field_errors[0]

        # assert that field errors are added if supports_expiration is True but expiration fields are not set
        request.POST.update(dict(expiration_days=0, expiration_reenrollment_days=0, reenrollment_error_template=""))
        form = form_class(request.POST)

        assert not form.is_valid()
        error_dict = form.errors
        assert "expiration_days" in error_dict
        assert "expiration_reenrollment_days" in error_dict
        assert "reenrollment_error_template" in error_dict

    def test_EnrollmentFlowForm_clean_supports_expiration_staff_user(
        self, admin_user_request, flow_admin_model, model_TransitAgency, model_IdentityGatewayConfig
    ):
        model_TransitAgency.slug = "cst"  # use value that will map to existing templates
        model_TransitAgency.save()

        request = admin_user_request(user_type="staff")

        form_class = flow_admin_model.get_form(request)

        request.POST = dict(
            system_name="senior",  # use value that will map to existing templates
            supported_enrollment_methods=[models.EnrollmentMethods.DIGITAL, models.EnrollmentMethods.IN_PERSON],
            transit_agency=model_TransitAgency.id,
            supports_expiration=True,
        )

        # fake a valid claims configuration
        request.POST.update(
            dict(
                oauth_config=model_IdentityGatewayConfig.id,
            )
        )

        # assert that field errors are added if supports_expiration is True but expiration fields are not set
        request.POST.update(dict(expiration_days=0, expiration_reenrollment_days=0))
        form = form_class(request.POST)

        assert not form.is_valid()
        error_dict = form.errors
        assert "expiration_days" in error_dict
        assert "expiration_reenrollment_days" in error_dict
