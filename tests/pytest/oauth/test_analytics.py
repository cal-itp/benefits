import pytest

from benefits.oauth.analytics import FinishedSignInEvent, OAuthErrorEvent, OAuthEvent


@pytest.mark.django_db
def test_OAuthEvent_flow_client_name_when_uses_claims_verification(app_request, mocked_session_flow_uses_claims_verification):
    mocked_flow = mocked_session_flow_uses_claims_verification(app_request)
    mocked_flow.oauth_config.client_name = "ClientName"

    event = OAuthEvent(app_request, "event type")

    assert "claims_provider" in event.event_properties
    assert event.event_properties["claims_provider"] == mocked_flow.oauth_config.client_name


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow_does_not_use_claims_verification")
def test_OAuthEvent_flow_no_client_name_when_does_not_use_claims_verification(app_request):
    event = OAuthEvent(app_request, "event type")

    assert "claims_provider" not in event.event_properties


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow_uses_claims_verification")
def test_OAuthErrorEvent(app_request):
    event_default = OAuthErrorEvent(app_request, "the message", "the operation")

    assert event_default.event_type == "oauth error"
    assert event_default.event_properties["message"] == "the message"
    assert event_default.event_properties["operation"] == "the operation"


@pytest.mark.django_db
def test_FinishedSignInEvent_with_error(app_request):
    event = FinishedSignInEvent(app_request, error=10)
    assert event.event_properties["error_code"] == 10


@pytest.mark.django_db
def test_FinishedSignInEvent_without_error(app_request):
    event = FinishedSignInEvent(app_request)
    assert "error_code" not in event.event_properties
