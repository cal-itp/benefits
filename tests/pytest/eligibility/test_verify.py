import pytest

from benefits.eligibility.forms import EligibilityVerificationForm
from benefits.eligibility.verify import typenames_to_verify, eligibility_from_api, eligibility_from_oauth


@pytest.fixture
def form(mocker):
    return mocker.Mock(spec=EligibilityVerificationForm, cleaned_data={"name": "Garcia", "sub": "A1234567"})


@pytest.fixture
def mock_api_client_verify(mocker):
    return mocker.patch("benefits.eligibility.verify.Client.verify")


@pytest.mark.django_db
def test_typenames_to_verify(model_TransitAgency, model_EligibilityVerifier):
    expected = [t.name for t in model_TransitAgency.types_to_verify(model_EligibilityVerifier)]

    result = typenames_to_verify(model_TransitAgency, model_EligibilityVerifier)

    assert result == expected


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
def test_eligibility_from_oauth_auth_not_required(mocked_session_verifier_auth_not_required, model_TransitAgency):
    # mocked_session_verifier_auth_not_required is Mocked version of the session.verifier() function
    # call it (with a None request) to return a verifier object
    verifier = mocked_session_verifier_auth_not_required(None)

    types = eligibility_from_oauth(verifier, "claim", model_TransitAgency)

    assert types == []


@pytest.mark.django_db
def test_eligibility_from_oauth_auth_claim_mismatch(mocked_session_verifier_auth_required, model_TransitAgency):
    # mocked_session_verifier_auth_required is Mocked version of the session.verifier() function
    # call it (with a None request) to return a verifier object
    verifier = mocked_session_verifier_auth_required(None)
    verifier.auth_claim = "claim"

    types = eligibility_from_oauth(verifier, "some_other_claim", model_TransitAgency)

    assert types == []


@pytest.mark.django_db
def test_eligibility_from_oauth_auth_claim_match(
    mocked_session_verifier_auth_required, model_EligibilityType, model_TransitAgency
):
    # mocked_session_verifier_auth_required is Mocked version of the session.verifier() function
    # call it (with a None request) to return a verifier object
    verifier = mocked_session_verifier_auth_required.return_value
    verifier.auth_provider.claim = "claim"
    verifier.eligibility_type = model_EligibilityType

    types = eligibility_from_oauth(verifier, "claim", model_TransitAgency)

    assert types == [model_EligibilityType.name]
