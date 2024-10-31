from unittest.mock import create_autospec
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from django.middleware.locale import LocaleMiddleware
from django.utils import timezone

import pytest

from pytest_socket import disable_socket

from benefits.core import session
from benefits.core.models import ClaimsProvider, EnrollmentFlow, TransitProcessor, PemData, TransitAgency


def pytest_runtest_setup():
    disable_socket()


@pytest.fixture
def app_request(rf):
    """
    Fixture creates and initializes a new Django request object similar to a real application request.
    """
    # create a request for the path, initialize
    app_request = rf.get("/some/arbitrary/path")

    # https://stackoverflow.com/a/55530933/358804
    middleware = [SessionMiddleware(lambda x: x), LocaleMiddleware(lambda x: x)]
    for m in middleware:
        m.process_request(app_request)

    app_request.session.save()
    session.reset(app_request)

    return app_request


@pytest.fixture
def model_User():
    return User.objects.create(is_active=True, is_staff=True, first_name="Test", last_name="User")


# autouse this fixture so we never call out to the real secret store
@pytest.fixture(autouse=True)
def mock_models_get_secret_by_name(mocker):
    return mocker.patch("benefits.core.models.get_secret_by_name", return_value="secret value!")


@pytest.fixture
def model_PemData():
    data = PemData.objects.create(text_secret_name="pem-secret-data", label="Test public key")

    return data


@pytest.fixture
def model_ClaimsProvider():
    claims_provider = ClaimsProvider.objects.create(
        sign_out_button_template="core/includes/button--sign-out--senior.html",
        sign_out_link_template="core/includes/link--sign-out--senior.html",
        client_name="Client",
        client_id_secret_name="1234",
        authority="https://example.com",
    )

    return claims_provider


@pytest.fixture
def model_ClaimsProvider_no_sign_out(model_ClaimsProvider):
    model_ClaimsProvider.sign_out_button_template = None
    model_ClaimsProvider.sign_out_link_template = None
    model_ClaimsProvider.save()

    return model_ClaimsProvider


@pytest.fixture
def model_EnrollmentFlow(model_TransitAgency):
    flow = EnrollmentFlow.objects.create(
        system_name="test",
        selection_label_template_override="eligibility/includes/selection-label.html",
        eligibility_start_template_override="eligibility/start.html",
        eligibility_unverified_template_override="eligibility/unverified.html",
        label="Test flow label",
        group_id="group123",
        enrollment_index_template_override="enrollment/index.html",
        enrollment_success_template_override="enrollment/success.html",
        transit_agency=model_TransitAgency,
    )

    return flow


@pytest.fixture
def model_EnrollmentFlow_with_eligibility_api(model_EnrollmentFlow, model_PemData):
    model_EnrollmentFlow.eligibility_api_url = "https://example.com/verify"
    model_EnrollmentFlow.eligibility_api_auth_header = "X-API-AUTH"
    model_EnrollmentFlow.eligibility_api_auth_key_secret_name = "secret-key"
    model_EnrollmentFlow.eligibility_api_public_key = model_PemData
    model_EnrollmentFlow.eligibility_form_class = "benefits.eligibility.forms.CSTAgencyCard"
    model_EnrollmentFlow.save()

    return model_EnrollmentFlow


@pytest.fixture
def model_EnrollmentFlow_with_scope_and_claim(model_EnrollmentFlow, model_ClaimsProvider):
    model_EnrollmentFlow.claims_provider = model_ClaimsProvider
    model_EnrollmentFlow.claims_scope = "scope"
    model_EnrollmentFlow.claims_eligibility_claim = "claim"
    model_EnrollmentFlow.save()

    return model_EnrollmentFlow


@pytest.fixture
def model_EnrollmentFlow_with_claims_scheme(model_EnrollmentFlow_with_scope_and_claim, model_TransitAgency):
    model_EnrollmentFlow_with_scope_and_claim.claims_scheme_override = "scheme"
    model_EnrollmentFlow_with_scope_and_claim.transit_agency = model_TransitAgency
    model_EnrollmentFlow_with_scope_and_claim.save()

    return model_EnrollmentFlow_with_scope_and_claim


@pytest.fixture
def model_EnrollmentFlow_does_not_support_expiration(model_EnrollmentFlow):
    model_EnrollmentFlow.supports_expiration = False
    model_EnrollmentFlow.expiration_days = 0
    model_EnrollmentFlow.save()

    return model_EnrollmentFlow


@pytest.fixture
def model_EnrollmentFlow_zero_expiration_days(model_EnrollmentFlow):
    model_EnrollmentFlow.supports_expiration = True
    model_EnrollmentFlow.expiration_days = 0
    model_EnrollmentFlow.expiration_reenrollment_days = 14
    model_EnrollmentFlow.save()

    return model_EnrollmentFlow


@pytest.fixture
def model_EnrollmentFlow_zero_expiration_reenrollment_days(model_EnrollmentFlow):
    model_EnrollmentFlow.supports_expiration = True
    model_EnrollmentFlow.expiration_days = 14
    model_EnrollmentFlow.expiration_reenrollment_days = 0
    model_EnrollmentFlow.save()

    return model_EnrollmentFlow


@pytest.fixture
def model_EnrollmentFlow_supports_expiration(model_EnrollmentFlow):
    model_EnrollmentFlow.supports_expiration = True
    model_EnrollmentFlow.expiration_days = 365
    model_EnrollmentFlow.expiration_reenrollment_days = 14
    model_EnrollmentFlow.reenrollment_error_template = "enrollment/reenrollment-error--calfresh.html"
    model_EnrollmentFlow.save()

    return model_EnrollmentFlow


@pytest.fixture
def model_TransitProcessor():
    transit_processor = TransitProcessor.objects.create(
        name="Test Transit Processor",
        api_base_url="https://example.com/enrollments",
        card_tokenize_url="https://example.com/enrollments/card-tokenize.js",
        card_tokenize_func="tokenize",
        card_tokenize_env="test",
    )

    return transit_processor


@pytest.fixture
def model_TransitAgency(model_PemData, model_TransitProcessor):
    agency = TransitAgency.objects.create(
        slug="test",
        short_name="TEST",
        long_name="Test Transit Agency",
        info_url="https://example.com/test-agency",
        phone="800-555-5555",
        active=True,
        transit_processor=model_TransitProcessor,
        transit_processor_client_id="client_id",
        transit_processor_client_secret_name="client_secret_name",
        transit_processor_audience="audience",
        eligibility_api_id="test123",
        eligibility_api_private_key=model_PemData,
        eligibility_api_public_key=model_PemData,
        eligibility_api_jws_signing_alg="alg",
        index_template_override="core/agency-index.html",
        eligibility_index_template_override="eligibility/index.html",
        logo_large="agencies/cst-lg.png",
        logo_small="agencies/cst-sm.png",
    )

    return agency


@pytest.fixture
def model_TransitAgency_inactive(model_TransitAgency):
    model_TransitAgency.active = False
    model_TransitAgency.save()

    return model_TransitAgency


@pytest.fixture
def mocked_analytics_module(mocker):
    """
    Fixture returns a helper function to mock the analytics module imported on another given module.
    """

    def mock(module):
        return mocker.patch.object(module, "analytics")

    return mock


@pytest.fixture
def mocked_view():
    def test_view(request):
        pass

    return create_autospec(test_view)


@pytest.fixture
def mocked_session_agency(mocker, model_TransitAgency):
    return mocker.patch("benefits.core.session.agency", autospec=True, return_value=model_TransitAgency)


@pytest.fixture
def mocked_session_eligible(mocker):
    return mocker.patch("benefits.core.session.eligible", autospec=True, return_value=True)


@pytest.fixture
def mocked_session_oauth_token(mocker):
    return mocker.patch("benefits.core.session.oauth_token", autospec=True, return_value="token")


@pytest.fixture
def mocked_session_enrollment_expiry(mocker):
    return mocker.patch(
        "benefits.core.session.enrollment_expiry",
        autospec=True,
        return_value=timezone.make_aware(timezone.datetime(2024, 1, 1), timezone=timezone.get_default_timezone()),
    )


@pytest.fixture
def mocked_session_flow(mocker, model_EnrollmentFlow):
    return mocker.patch("benefits.core.session.flow", autospec=True, return_value=model_EnrollmentFlow)


@pytest.fixture
def mocked_session_flow_uses_claims_verification(mocked_session_flow, model_EnrollmentFlow_with_scope_and_claim):
    mocked_session_flow.return_value = model_EnrollmentFlow_with_scope_and_claim
    return mocked_session_flow


@pytest.fixture
def mocked_session_flow_does_not_use_claims_verification(mocked_session_flow, model_EnrollmentFlow_with_eligibility_api):
    mocked_session_flow.return_value = model_EnrollmentFlow_with_eligibility_api
    return mocked_session_flow


@pytest.fixture
def mocked_session_reset(mocker):
    return mocker.patch("benefits.core.session.reset")


@pytest.fixture
def mocked_session_update(mocker):
    return mocker.patch("benefits.core.session.update")


@pytest.fixture
def mocked_session_oauth_extra_claims(mocker):
    return mocker.patch("benefits.core.session.oauth_extra_claims")
