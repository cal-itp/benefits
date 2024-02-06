from unittest.mock import create_autospec
from django.contrib.sessions.middleware import SessionMiddleware
from django.middleware.locale import LocaleMiddleware

import pytest
from pytest_socket import disable_socket

from benefits.core import session
from benefits.core.models import AuthProvider, EligibilityType, EligibilityVerifier, PaymentProcessor, PemData, TransitAgency


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


# autouse this fixture so we never call out to the real secret store
@pytest.fixture(autouse=True)
def mock_models_get_secret_by_name(mocker):
    return mocker.patch("benefits.core.models.get_secret_by_name", return_value="secret value!")


@pytest.fixture
def model_PemData():
    data = PemData.objects.create(
        text="-----BEGIN PUBLIC KEY-----\nPEM DATA\n-----END PUBLIC KEY-----\n", label="Test public key"
    )

    return data


@pytest.fixture
def model_AuthProvider():
    auth_provider = AuthProvider.objects.create(
        sign_out_button_template="core/includes/button--sign-out--senior.html",
        sign_out_link_template="core/includes/link--sign-out--senior.html",
        client_name="Client",
        client_id_secret_name="1234",
        authority="https://example.com",
    )

    return auth_provider


@pytest.fixture
def model_AuthProvider_with_verification(model_AuthProvider):
    model_AuthProvider.scope = "scope"
    model_AuthProvider.claim = "claim"
    model_AuthProvider.save()

    return model_AuthProvider


@pytest.fixture
def model_AuthProvider_with_verification_no_sign_out(model_AuthProvider):
    model_AuthProvider.scope = "scope"
    model_AuthProvider.claim = "claim"
    model_AuthProvider.sign_out_button_template = None
    model_AuthProvider.sign_out_link_template = None
    model_AuthProvider.save()

    return model_AuthProvider


@pytest.fixture
def model_AuthProvider_without_verification(model_AuthProvider):
    model_AuthProvider.scope = None
    model_AuthProvider.claim = None
    model_AuthProvider.save()

    return model_AuthProvider


@pytest.fixture
def model_AuthProvider_without_verification_no_sign_out(model_AuthProvider):
    model_AuthProvider.scope = None
    model_AuthProvider.claim = None
    model_AuthProvider.sign_out_button_template = None
    model_AuthProvider.sign_out_link_template = None
    model_AuthProvider.save()

    return model_AuthProvider


@pytest.fixture
def model_EligibilityType():
    eligibility = EligibilityType.objects.create(name="test", label="Test Eligibility Type", group_id="1234")

    return eligibility


@pytest.fixture
def model_EligibilityVerifier(model_PemData, model_EligibilityType):
    verifier = EligibilityVerifier.objects.create(
        name="Test Verifier",
        active=True,
        api_url="https://example.com/verify",
        api_auth_header="X-API-AUTH",
        api_auth_key_secret_name="secret-key",
        eligibility_type=model_EligibilityType,
        public_key=model_PemData,
        selection_label_template="eligibility/includes/selection-label.html",
    )

    return verifier


@pytest.fixture
def model_EligibilityVerifier_AuthProvider_with_verification(model_AuthProvider_with_verification, model_EligibilityVerifier):
    model_EligibilityVerifier.auth_provider = model_AuthProvider_with_verification
    model_EligibilityVerifier.save()

    return model_EligibilityVerifier


@pytest.fixture
def model_PaymentProcessor(model_PemData):
    payment_processor = PaymentProcessor.objects.create(
        name="Test Payment Processor",
        api_base_url="https://example.com/payments",
        api_access_token_endpoint="token",
        api_access_token_request_key="X-API-TOKEN",
        api_access_token_request_val="secret-value",
        card_tokenize_url="https://example.com/payments/tokenize.js",
        card_tokenize_func="tokenize",
        card_tokenize_env="test",
        client_cert=model_PemData,
        client_cert_private_key=model_PemData,
        client_cert_root_ca=model_PemData,
        customer_endpoint="customer",
        customers_endpoint="customers",
        group_endpoint="group",
    )

    return payment_processor


@pytest.fixture
def model_TransitAgency(model_PemData, model_EligibilityType, model_EligibilityVerifier, model_PaymentProcessor):
    agency = TransitAgency.objects.create(
        slug="test",
        short_name="TEST",
        long_name="Test Transit Agency",
        agency_id="test123",
        merchant_id="test",
        info_url="https://example.com/test-agency",
        phone="800-555-5555",
        active=True,
        payment_processor=model_PaymentProcessor,
        private_key=model_PemData,
        public_key=model_PemData,
        jws_signing_alg="alg",
        index_template="core/agency-index.html",
        eligibility_index_template="eligibility/index.html",
        enrollment_success_template="enrollment/success.html",
    )

    # add many-to-many relationships after creation, need ID on both sides
    agency.eligibility_types.add(model_EligibilityType)
    agency.eligibility_verifiers.add(model_EligibilityVerifier)
    agency.save()

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
def mocked_session_eligibility(mocker, model_EligibilityType):
    mocker.patch("benefits.core.session.eligible", autospec=True, return_value=True)
    return mocker.patch("benefits.core.session.eligibility", autospec=True, return_value=model_EligibilityType)


@pytest.fixture
def mocked_session_oauth_token(mocker):
    return mocker.patch("benefits.core.session.oauth_token", autospec=True, return_value="token")


@pytest.fixture
def mocked_session_verifier(mocker, model_EligibilityVerifier):
    return mocker.patch("benefits.core.session.verifier", autospec=True, return_value=model_EligibilityVerifier)


@pytest.fixture
def mocked_session_verifier_oauth(mocker, model_EligibilityVerifier_AuthProvider_with_verification):
    return mocker.patch(
        "benefits.core.session.verifier", autospec=True, return_value=model_EligibilityVerifier_AuthProvider_with_verification
    )


@pytest.fixture
def mocked_session_verifier_auth_required(
    mocker, model_EligibilityVerifier_AuthProvider_with_verification, mocked_session_verifier_oauth
):
    mock_verifier = mocker.Mock(spec=model_EligibilityVerifier_AuthProvider_with_verification)
    mock_verifier.name = model_EligibilityVerifier_AuthProvider_with_verification.name
    mock_verifier.is_auth_required = True
    mock_verifier.auth_provider.sign_out_button_template = (
        model_EligibilityVerifier_AuthProvider_with_verification.auth_provider.sign_out_button_template
    )
    mock_verifier.auth_provider.sign_out_link_template = (
        model_EligibilityVerifier_AuthProvider_with_verification.auth_provider.sign_out_link_template
    )
    mocked_session_verifier_oauth.return_value = mock_verifier
    return mocked_session_verifier_oauth


@pytest.fixture
def mocked_session_verifier_auth_not_required(mocked_session_verifier_auth_required):
    # mocked_session_verifier_auth_required.return_value is the Mock(spec=model_EligibilityVerifier) from that fixture
    mocked_session_verifier_auth_required.return_value.is_auth_required = False
    mocked_session_verifier_auth_required.return_value.uses_auth_verification = False
    return mocked_session_verifier_auth_required


@pytest.fixture
def mocked_session_update(mocker):
    return mocker.patch("benefits.eligibility.views.session.update")
