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
def test_eligibility_from_api_error(mocker, model_TransitAgency, model_EligibilityVerifier, mock_api_client_verify, form):
    api_errors = {"name": "Name error"}
    api_response = mocker.Mock(error=api_errors)
    mock_api_client_verify.return_value = api_response

    response = eligibility_from_api(model_EligibilityVerifier, form, model_TransitAgency)

    assert response is None


@pytest.mark.django_db
def test_eligibility_from_api_verified_types(
    mocker, model_TransitAgency, model_EligibilityVerifier, mock_api_client_verify, form
):
    verified_types = ["type1", "type2"]
    api_response = mocker.Mock(eligibility=verified_types, error=None)
    mock_api_client_verify.return_value = api_response

    response = eligibility_from_api(model_EligibilityVerifier, form, model_TransitAgency)

    assert response == verified_types


@pytest.mark.django_db
def test_eligibility_from_api_no_verified_types(
    mocker, model_TransitAgency, model_EligibilityVerifier, mock_api_client_verify, form
):
    verified_types = []
    api_response = mocker.Mock(eligibility=verified_types, error=None)
    mock_api_client_verify.return_value = api_response

    response = eligibility_from_api(model_EligibilityVerifier, form, model_TransitAgency)

    assert response == verified_types


@pytest.mark.django_db
def test_eligibility_from_oauth_does_not_use_claims_verification(
    mocked_session_verifier_does_not_use_claims_verification, model_TransitAgency
):
    # mocked_session_verifier_does_not_use_claims_verification is Mocked version of the session.verifier() function
    # call it (with a None request) to return a verifier object
    verifier = mocked_session_verifier_does_not_use_claims_verification(None)

    types = eligibility_from_oauth(verifier, "claim", model_TransitAgency)

    assert types == []


@pytest.mark.django_db
def test_eligibility_from_oauth_claim_mismatch(mocked_session_verifier_uses_claims_verification, model_TransitAgency):
    # mocked_session_verifier_uses_claims_verification is Mocked version of the session.verifier() function
    # call it (with a None request) to return a verifier object
    verifier = mocked_session_verifier_uses_claims_verification(None)
    verifier.claim = "claim"

    types = eligibility_from_oauth(verifier, "some_other_claim", model_TransitAgency)

    assert types == []


@pytest.mark.django_db
def test_eligibility_from_oauth_claim_match(
    mocked_session_verifier_uses_claims_verification, model_EligibilityType, model_TransitAgency
):
    # mocked_session_verifier_uses_claims_verification is Mocked version of the session.verifier() function
    # call it (with a None request) to return a verifier object
    verifier = mocked_session_verifier_uses_claims_verification.return_value
    verifier.claims_claim = "claim"
    verifier.eligibility_type = model_EligibilityType

    types = eligibility_from_oauth(verifier, "claim", model_TransitAgency)

    assert types == [model_EligibilityType.name]
