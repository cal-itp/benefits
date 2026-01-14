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
            ("staff", ()),
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

    def test_EnrollmentFlowForm_no_transit_agency(self, admin_user_request):
        request = admin_user_request()

        request.POST = dict(
            system_name="senior",
            supported_enrollment_methods=[models.EnrollmentMethods.DIGITAL, models.EnrollmentMethods.IN_PERSON],
        )

        # get the Form class that's used in the admin add view as the user would see it
        form_class = self.model_admin.get_form(request)
        form = form_class(request.POST)

        assert not form.errors
        assert form.is_valid()

    def test_EnrollmentFlowForm_no_request_config(self, admin_user_request, model_TransitAgency):
        request = admin_user_request()

        # fill out the form without EligibilityApiVerificationRequest nor ClaimsVerificationRequest
        request.POST = dict(
            system_name="senior",  # use value that will map to existing templates
            supported_enrollment_methods=[models.EnrollmentMethods.DIGITAL, models.EnrollmentMethods.IN_PERSON],
            transit_agency=model_TransitAgency.id,
        )

        form_class = self.model_admin.get_form(request)
        form = form_class(request.POST)

        assert not form.is_valid()
        error_dict = form.errors
        assert (
            "Must configure either claims verification or Eligibility API verification before adding to a transit agency."
            in error_dict["__all__"]
        )

    def test_EnrollmentFlowForm_supports_expiration(
        self, admin_user_request, model_TransitAgency, model_IdentityGatewayConfig, model_ClaimsVerificationRequest
    ):
        request = admin_user_request()

        request.POST = dict(
            system_name="senior",  # use value that will map to existing templates
            supported_enrollment_methods=[models.EnrollmentMethods.DIGITAL, models.EnrollmentMethods.IN_PERSON],
            transit_agency=model_TransitAgency.id,
            supports_expiration=True,
            # invalid expiration data when supports_expiration is True
            expiration_days=0,
            expiration_reenrollment_days=0,
            # valid claims configuration
            oauth_config=model_IdentityGatewayConfig.id,
            claims_request=model_ClaimsVerificationRequest.id,
        )

        form_class = self.model_admin.get_form(request)
        form = form_class(request.POST)

        assert not form.is_valid()
        error_dict = form.errors
        assert "expiration_days" in error_dict
        assert "expiration_reenrollment_days" in error_dict
