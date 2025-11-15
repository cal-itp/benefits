import pytest

from django.contrib import admin

from benefits.core import models
from benefits.core.admin.enrollment import EnrollmentEventAdmin, SortableEnrollmentFlowAdmin
from benefits.core.admin.mixins import ProdReadOnlyPermissionMixin, StaffPermissionMixin


@pytest.mark.django_db
class TestEnrollmentEventAdmin:
    @pytest.fixture(autouse=True)
    def init(self):
        self.model_admin = EnrollmentEventAdmin(models.EnrollmentEvent, admin.site)

    def test_permissions_mixin(self):
        assert isinstance(self.model_admin, ProdReadOnlyPermissionMixin)


@pytest.mark.django_db
class TestEnrollmentFlowAdmin:

    @pytest.fixture(autouse=True)
    def init(self):
        self.model_admin = SortableEnrollmentFlowAdmin(models.EnrollmentFlow, admin.site)

    def test_permissions_mixin(self):
        assert isinstance(self.model_admin, StaffPermissionMixin)

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
    def test_get_exclude(self, admin_user_request, user_type, expected):
        if expected:
            model_fields = [f.name for f in self.model_admin.model._meta.get_fields()]
            assert all(field in model_fields for field in expected)

        request = admin_user_request(user_type)

        excluded = self.model_admin.get_exclude(request)

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
                    "selection_label_template_override",
                ],
            ),
            ("super", ()),
        ],
    )
    def test_get_readonly_fields(self, admin_user_request, user_type, expected):
        if expected:
            model_fields = [f.name for f in self.model_admin.model._meta.get_fields()]
            assert all(field in model_fields for field in expected)

        request = admin_user_request(user_type)

        readonly = self.model_admin.get_readonly_fields(request)

        assert set(readonly) == set(expected)

    def test_EnrollmentFlowForm_staff_member_no_transit_agency(self, admin_user_request):
        request = admin_user_request()

        # get the Form class that's used in the admin add view as the user would see it
        form_class = self.model_admin.get_form(request)

        request.POST = dict(
            system_name="senior",
            supported_enrollment_methods=[models.EnrollmentMethods.DIGITAL, models.EnrollmentMethods.IN_PERSON],
        )

        form = form_class(request.POST)
        assert not form.errors
        assert form.is_valid()

    @pytest.mark.parametrize("active", [True, False])
    def test_EnrollmentFlowForm_staff_member_with_transit_agency(self, admin_user_request, model_TransitAgency, active):
        model_TransitAgency.active = active
        model_TransitAgency.slug = "mst"  # use value that will map to existing templates
        model_TransitAgency.save()

        request = admin_user_request()

        # get the Form class that's used in the admin add view as the user would see it
        form_class = self.model_admin.get_form(request)

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

    def test_EnrollmentFlowForm_clean_eligibility_api_verification(self, admin_user_request, model_TransitAgency):
        model_TransitAgency.slug = "cst"  # use value that will map to existing templates
        model_TransitAgency.save()

        request = admin_user_request("super")

        # fill out the form without a transit agency
        request.POST = dict(
            system_name="senior",  # use value that will map to existing templates
            supported_enrollment_methods=[models.EnrollmentMethods.DIGITAL, models.EnrollmentMethods.IN_PERSON],
            eligibility_api_url="http://server:8000/verify",
            eligibility_api_auth_header="",
            eligibility_api_auth_key_secret_name="",
            eligibility_api_jwe_cek_enc="",
            eligibility_api_jwe_encryption_alg="",
            eligibility_api_jws_signing_alg="",
            eligibility_api_public_key=None,
        )

        form_class = self.model_admin.get_form(request)

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
        model_TransitAgency,
        model_IdentityGatewayConfig,
        model_ClaimsVerificationRequest,
    ):
        model_TransitAgency.slug = "cst"  # use value that will map to existing templates
        model_TransitAgency.active = False
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

        form_class = self.model_admin.get_form(request)
        form = form_class(request.POST)

        # assert that field errors are added if supports_expiration is True but expiration fields are not set
        request.POST.update(dict(expiration_days=0, expiration_reenrollment_days=0))
        form = form_class(request.POST)

        assert not form.is_valid()
        error_dict = form.errors
        assert "expiration_days" in error_dict
        assert "expiration_reenrollment_days" in error_dict

    def test_EnrollmentFlowForm_clean_supports_expiration_staff_user(
        self, admin_user_request, model_TransitAgency, model_IdentityGatewayConfig
    ):
        model_TransitAgency.slug = "cst"  # use value that will map to existing templates
        model_TransitAgency.save()

        request = admin_user_request(user_type="staff")

        form_class = self.model_admin.get_form(request)

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
