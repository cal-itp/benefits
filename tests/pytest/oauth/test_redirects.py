from benefits.oauth.redirects import deauthorize_redirect, generate_redirect_uri


def test_deauthorize_redirect(mocked_oauth_client):
    mocked_oauth_client.load_server_metadata.return_value = {"end_session_endpoint": "https://server/endsession"}

    result = deauthorize_redirect("token", "https://localhost/redirect_uri")

    mocked_oauth_client.load_server_metadata.assert_called()
    assert result.status_code == 302
    assert (
        result.url
        == "https://server/endsession?id_token_hint=token&post_logout_redirect_uri=https%3A%2F%2Flocalhost%2Fredirect_uri"
    )


def test_generate_redirect_uri_default(rf):
    request = rf.get("/oauth/login")
    path = "/test"

    redirect_uri = generate_redirect_uri(request, path)

    assert redirect_uri == "https://testserver/test"


def test_generate_redirect_uri_localhost(rf):
    request = rf.get("/oauth/login", SERVER_NAME="localhost")
    path = "/test"

    redirect_uri = generate_redirect_uri(request, path)

    assert redirect_uri == "http://localhost/test"
