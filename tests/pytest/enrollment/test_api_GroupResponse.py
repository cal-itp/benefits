import pytest

from benefits.enrollment.api import ApiError, GroupResponse


def test_no_payload_invalid_response(mocker):
    mock_response = mocker.Mock()
    mock_response.json.side_effect = ValueError

    with pytest.raises(ApiError, match=r"response"):
        GroupResponse(mock_response, "customer", "group")


def test_no_payload_valid_response_single_matching_id(mocker):
    mock_response = mocker.Mock()
    mock_response.json.return_value = ["0"]

    response = GroupResponse(mock_response, "0", "group")

    assert response.customer_ids == ["0"]
    assert response.updated_customer_id == "0"
    assert response.success
    assert response.message == ""


def test_no_payload_valid_response_single_unmatching_id(mocker):
    mock_response = mocker.Mock()
    mock_response.json.return_value = ["1"]

    response = GroupResponse(mock_response, "0", "group")

    assert response.customer_ids == ["1"]
    assert response.updated_customer_id == "1"
    assert not response.success
    assert "customer_id" in response.message


def test_no_payload_valid_response_multiple_ids(mocker):
    mock_response = mocker.Mock()
    mock_response.json.return_value = ["0", "1"]

    response = GroupResponse(mock_response, "0", "group")

    assert response.customer_ids == ["0", "1"]
    assert not response.updated_customer_id
    assert not response.success
    assert "customer_id" in response.message


@pytest.mark.parametrize("exception", [KeyError, ValueError])
def test_payload_invalid_response(mocker, exception):
    mock_response = mocker.Mock()
    mock_response.json.side_effect = exception

    with pytest.raises(ApiError, match=r"response"):
        GroupResponse(mock_response, "0", "group", [])


def test_payload_valid_response(mocker):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"errors": [{"detail": "0 group"}]}

    response = GroupResponse(mock_response, "0", "group", ["0"])

    assert response.customer_ids == ["0"]
    assert response.updated_customer_id == "0"
    assert response.success
    assert response.message == ""


failure_conditions = [
    # detail is None
    ({"detail": None}, ["0"]),
    # customer_id is None
    ({"detail": "0 group"}, [None]),
    # customer_id not in detail
    ({"detail": "1 group"}, ["0"]),
    # group_id not in detail
    ({"detail": "0"}, ["0"]),
]


@pytest.mark.parametrize("error,payload", failure_conditions)
def test_payload_failure_response(mocker, error, payload):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"errors": [error]}

    with pytest.raises(ApiError, match=r"response"):
        GroupResponse(mock_response, "0", "group", payload)
