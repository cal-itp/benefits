import pytest

from benefits.eligibility.forms import EligibilityVerificationForm
from benefits.eligibility.verify import eligibility_from_api, eligibility_from_oauth


@pytest.fixture
def form(mocker):
    return mocker.Mock(spec=EligibilityVerificationForm, cleaned_data={"name": "Garcia", "sub": "A1234567"})


@pytest.fixture
def mock_api_client_verify(mocker):
    return mocker.patch("benefits.eligibility.verify.Client.verify")


@pytest.mark.django_db
def test_eligibility_from_api_error(mocker, model_TransitAgency, model_EnrollmentFlow, mock_api_client_verify, form):
    api_errors = {"name": "Name error"}
    api_response = mocker.Mock(error=api_errors)
    mock_api_client_verify.return_value = api_response

    response = eligibility_from_api(model_EnrollmentFlow, form, model_TransitAgency)

    assert response is None


@pytest.mark.django_db
def test_eligibility_from_api_verified_types(mocker, model_TransitAgency, model_EnrollmentFlow, mock_api_client_verify, form):
    verified_types = ["Test Flow"]
    api_response = mocker.Mock(eligibility=verified_types, error=None)
    mock_api_client_verify.return_value = api_response

    response = eligibility_from_api(model_EnrollmentFlow, form, model_TransitAgency)

    assert response is True


@pytest.mark.django_db
def test_eligibility_from_api_no_verified_types(
    mocker, model_TransitAgency, model_EnrollmentFlow, mock_api_client_verify, form
):
    verified_types = []
    api_response = mocker.Mock(eligibility=verified_types, error=None)
    mock_api_client_verify.return_value = api_response

    response = eligibility_from_api(model_EnrollmentFlow, form, model_TransitAgency)

    assert response is False


@pytest.mark.django_db
def test_eligibility_from_oauth_does_not_use_claims_verification(
    mocked_session_flow_does_not_use_claims_verification, model_TransitAgency
):
    # mocked_session_flow_does_not_use_claims_verification is Mocked version of the session.flow() function
    flow = mocked_session_flow_does_not_use_claims_verification.return_value

    response = eligibility_from_oauth(flow, "claim", model_TransitAgency)

    assert response is False


@pytest.mark.django_db
def test_eligibility_from_oauth_claim_mismatch(mocked_session_flow_uses_claims_verification, model_TransitAgency):
    # mocked_session_flow_uses_claims_verification is Mocked version of the session.flow() function
    flow = mocked_session_flow_uses_claims_verification.return_value
    flow.claims_claim = "claim"

    response = eligibility_from_oauth(flow, "some_other_claim", model_TransitAgency)

    assert response is False


@pytest.mark.django_db
def test_eligibility_from_oauth_claim_match(mocked_session_flow_uses_claims_verification, model_TransitAgency):
    # mocked_session_flow_uses_claims_verification is Mocked version of the session.flow() function
    flow = mocked_session_flow_uses_claims_verification.return_value
    flow.claims_claim = "claim"

    response = eligibility_from_oauth(flow, "claim", model_TransitAgency)

    assert response is True
