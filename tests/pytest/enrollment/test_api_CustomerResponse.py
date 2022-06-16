import pytest

from benefits.enrollment.api import ApiError, CustomerResponse


@pytest.mark.parametrize("exception", [KeyError, ValueError])
def test_invalid_response(mocker, exception):
    mock_response = mocker.Mock()
    mock_response.json.side_effect = exception

    with pytest.raises(ApiError, match=r"response"):
        CustomerResponse(mock_response)


def test_no_id(mocker):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"id": None}

    with pytest.raises(ApiError, match=r"response"):
        CustomerResponse(mock_response)


def test_is_registered_default(mocker):
    id = "12345"
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"id": id}

    response = CustomerResponse(mock_response)

    assert response.id == id
    assert not response.is_registered


@pytest.mark.parametrize("is_registered", ["true", "True", "tRuE"])
def test_is_registered(mocker, is_registered):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"id": "12345", "is_registered": is_registered}

    response = CustomerResponse(mock_response)

    assert response.is_registered


@pytest.mark.parametrize("is_registered", ["false", "Frue", "fAlSe"])
def test_is_not_registered(mocker, is_registered):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"id": "12345", "is_registered": is_registered}

    response = CustomerResponse(mock_response)

    assert not response.is_registered
