from django.http import HttpResponse

from benefits.core import session
from benefits.oauth.views import logout

import pytest


@pytest.mark.request_path("/oauth/logout")
def test_logout(mocker, session_request):
    # logout internally calls _deauthorize_redirect
    # this mocks that function and a success response
    # and returns a spy object we can use to validate calls
    message = "logout successful"
    spy = mocker.patch("benefits.oauth.views._deauthorize_redirect", return_value=HttpResponse(message))

    token = "token"
    session.update(session_request, oauth_token=token)
    assert session.oauth_token(session_request) == token

    result = logout(session_request)

    spy.assert_called_with(token, "http://testserver/oauth/post_logout")
    assert result.status_code == 200
    assert message in str(result.content)
    assert session.oauth_token(session_request) is False
