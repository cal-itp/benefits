import pytest

from benefits.oauth.analytics import OAuthEvent


@pytest.mark.django_db
def test_OAuthEvent_checks_verifier_uses_auth_verification(app_request, mocked_session_verifier_uses_auth_verification):
    mocked_verifier = mocked_session_verifier_uses_auth_verification(app_request)

    OAuthEvent(app_request, "event type")

    mocked_verifier.uses_auth_verification.assert_called_once


@pytest.mark.django_db
def test_OAuthEvent_verifier_client_name_when_uses_auth_verification(
    app_request, mocked_session_verifier_uses_auth_verification
):
    mocked_verifier = mocked_session_verifier_uses_auth_verification(app_request)
    mocked_verifier.auth_provider.client_name = "ClientName"

    event = OAuthEvent(app_request, "event type")

    assert "auth_provider" in event.event_properties
    assert event.event_properties["auth_provider"] == mocked_verifier.auth_provider.client_name


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier_does_not_use_auth_verification")
def test_OAuthEvent_verifier_no_client_name_when_does_not_use_auth_verification(app_request):
    event = OAuthEvent(app_request, "event type")

    assert "auth_provider" not in event.event_properties
