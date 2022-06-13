import time

import pytest

from benefits.enrollment.api import ApiError, AccessTokenResponse


def test_AccessTokenResponse_invalid_response(mocker):
    mock_response = mocker.Mock()
    mock_response.json.side_effect = ValueError

    with pytest.raises(ApiError, match=r"response"):
        AccessTokenResponse(mock_response)


def test_AccessTokenResponse_valid_response(mocker):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"access_token": "access123", "token_type": "mock"}

    response = AccessTokenResponse(mock_response)

    assert response.access_token == "access123"
    assert response.token_type == "mock"
    assert response.expiry is None


def test_AccessTokenResponse_valid_response_expires_in(mocker):
    expires_in = 100
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"expires_in": expires_in}

    start = time.time()
    response = AccessTokenResponse(mock_response)

    assert response.expiry >= start + expires_in
