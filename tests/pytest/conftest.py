from unittest.mock import create_autospec

import pytest
from cdt_identity.models import ClaimsVerificationRequest, IdentityGatewayConfig
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from django.middleware.locale import LocaleMiddleware
from django.utils import timezone
from pytest_socket import disable_socket

from benefits.core import session
from benefits.core.models import EligibilityApiVerificationRequest, EnrollmentFlow, Environment, PemData, TransitAgency
from benefits.enrollment_littlepay.models import LittlepayConfig, LittlepayGroup
from benefits.enrollment_switchio.models import SwitchioConfig, SwitchioGroup


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
def app_request_post(rf):
    """
    Fixture creates and initializes a new Django POST request object similar to a real application request.
    """
    # create a request for the path, initialize
    app_request = rf.post("/some/arbitrary/path")

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
def mock_get_secret_by_name(mocker):
    return mocker.patch("benefits.core.models.common.get_secret_by_name", return_value="secret value!")


@pytest.fixture
def model_PemData():
    data = PemData.objects.create(text_secret_name="pem-secret-data", label="Test public key")

    return data


@pytest.fixture
def model_IdentityGatewayConfig():
    identity_gateway_config = IdentityGatewayConfig.objects.create(
        client_name="Client",
        client_id="319efaea-615b-4cd4-958f-e6cd2fd31646",
        authority="https://example.com",
    )

    return identity_gateway_config


@pytest.fixture
def model_ClaimsVerificationRequest():
    claims_verification_request = ClaimsVerificationRequest.objects.create(
        system_name="senior",
        scopes="scope",
        eligibility_claim="claim",
    )

    return claims_verification_request


@pytest.fixture
def model_EligibilityApiVerificationRequest(model_PemData):
    api_request = EligibilityApiVerificationRequest.objects.create(
        label="agency_card",
        api_auth_header="X-API-AUTH",
        api_auth_key_secret_name="secret-key",
        api_jwe_cek_enc="cek-enc",
        api_jwe_encryption_alg="alg",
        api_jws_signing_alg="alg",
        client_private_key=model_PemData,
        client_public_key=model_PemData,
        api_public_key=model_PemData,
        api_url="https://example.com/verify",
    )

    return api_request


@pytest.fixture
def model_EnrollmentFlow(model_TransitAgency):
    flow = EnrollmentFlow.objects.create(
        system_name="senior",
        label="Test flow label",
        transit_agency=model_TransitAgency,
    )

    return flow


@pytest.fixture
def model_LittlepayGroup(model_EnrollmentFlow):
    return LittlepayGroup.objects.create(
        group_id="d0fe23fd-61d6-455f-8e19-808058603171",
        enrollment_flow=model_EnrollmentFlow,
    )


@pytest.fixture
def model_SwitchioGroup(model_EnrollmentFlow):
    return SwitchioGroup.objects.create(
        group_id="senior-discount",
        enrollment_flow=model_EnrollmentFlow,
    )


@pytest.fixture
def model_EnrollmentFlow_with_eligibility_api(model_EnrollmentFlow, model_EligibilityApiVerificationRequest):
    model_EnrollmentFlow.system_name = "agency_card"
    model_EnrollmentFlow.api_request = model_EligibilityApiVerificationRequest
    model_EnrollmentFlow.save()

    return model_EnrollmentFlow


@pytest.fixture
def model_EnrollmentFlow_with_scope_and_claim(
    model_EnrollmentFlow, model_IdentityGatewayConfig, model_ClaimsVerificationRequest
):
    model_EnrollmentFlow.oauth_config = model_IdentityGatewayConfig
    model_EnrollmentFlow.claims_request = model_ClaimsVerificationRequest
    model_EnrollmentFlow.save()

    return model_EnrollmentFlow


@pytest.fixture
def model_EnrollmentFlow_with_claims_scheme(model_EnrollmentFlow_with_scope_and_claim, model_TransitAgency):
    model_EnrollmentFlow_with_scope_and_claim.claims_request.scheme = "scheme"
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
def model_EnrollmentFlow_supports_expiration(model_EnrollmentFlow):
    model_EnrollmentFlow.supports_expiration = True
    model_EnrollmentFlow.expiration_days = 365
    model_EnrollmentFlow.expiration_reenrollment_days = 14
    model_EnrollmentFlow.save()

    return model_EnrollmentFlow


@pytest.fixture
def model_EnrollmentFlow_supports_sign_out(model_EnrollmentFlow):
    model_EnrollmentFlow.sign_out_button_template = "core/includes/button--sign-out--senior.html"
    model_EnrollmentFlow.sign_out_link_template = "core/includes/link--sign-out--senior.html"
    model_EnrollmentFlow.save()

    return model_EnrollmentFlow


@pytest.fixture
def model_LittlepayConfig(model_TransitAgency):
    littlepay_config = LittlepayConfig.objects.create(
        transit_agency=model_TransitAgency,
        environment=Environment.QA,
        client_id="client_id",
        client_secret_name="client_secret_name",
        audience="audience",
    )

    return littlepay_config


@pytest.fixture
def model_SwitchioConfig(model_PemData, model_TransitAgency):
    switchio_config = SwitchioConfig.objects.create(
        transit_agency=model_TransitAgency,
        environment=Environment.ACC,
        tokenization_api_key="api_key",
        tokenization_api_secret_name="apisecret",
        client_certificate=model_PemData,
        ca_certificate=model_PemData,
        private_key=model_PemData,
    )

    return switchio_config


@pytest.fixture
def model_TransitAgency():
    agency = TransitAgency.objects.create(
        slug="cst",
        short_name="TEST",
        long_name="Test Transit Agency",
        info_url="https://example.com/test-agency",
        phone="800-555-5555",
        active=True,
        logo="agencies/cst.png",
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
def mocked_session_logged_in(mocker):
    return mocker.patch("benefits.core.session.logged_in", autospec=True, return_value=True)


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
