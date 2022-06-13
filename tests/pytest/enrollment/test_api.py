import time

import pytest

from benefits.enrollment.api import ApiError, AccessTokenResponse, CustomerResponse


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


@pytest.mark.parametrize("exception", [KeyError, ValueError])
def test_CustomerResponse_invalid_response(mocker, exception):
    mock_response = mocker.Mock()
    mock_response.json.side_effect = exception

    with pytest.raises(ApiError, match=r"response"):
        CustomerResponse(mock_response)


def test_CustomerResponse_no_id(mocker):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"id": None}

    with pytest.raises(ApiError, match=r"response"):
        CustomerResponse(mock_response)


def test_CustomerResponse(mocker):
    id = "12345"
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"id": id}

    response = CustomerResponse(mock_response)

    assert response.id == id
    assert not response.is_registered


@pytest.mark.parametrize("is_registered", ["true", "True", "tRuE"])
def test_CustomerResponse_is_registered(mocker, is_registered):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"id": "12345", "is_registered": is_registered}

    response = CustomerResponse(mock_response)

    assert response.is_registered


@pytest.mark.parametrize("is_registered", ["false", "Frue", "fAlSe"])
def test_CustomerResponse_not_is_registered(mocker, is_registered):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"id": "12345", "is_registered": is_registered}

    response = CustomerResponse(mock_response)

    assert not response.is_registered
