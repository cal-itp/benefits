import requests

import pytest

from benefits.enrollment.api import ApiError, CustomerResponse, Client


REQUESTS_ERRORS = [requests.ConnectionError, requests.Timeout, requests.TooManyRedirects, requests.HTTPError]


def test_init_no_agency():
    with pytest.raises(ValueError, match=r"agency"):
        Client(None)


def test_init_no_payment_processor(mocker):
    mock_agency = mocker.Mock()
    mock_agency.payment_processor = None

    with pytest.raises(ValueError, match=r"payment_processor"):
        Client(mock_agency)


def test_init(mocker):
    mock_agency = mocker.Mock()
    mock_agency.payment_processor = mocker.Mock()

    client = Client(mock_agency)

    assert client.agency == mock_agency
    assert client.payment_processor == mock_agency.payment_processor


@pytest.mark.django_db
@pytest.mark.parametrize("exception", REQUESTS_ERRORS)
def test_access_token_exception(mocker, first_agency, exception):
    client = Client(first_agency)
    mock_response = mocker.Mock()
    mock_response.raise_for_status.side_effect = exception
    mocker.patch.object(client, "_post", return_value=mock_response)

    with pytest.raises(ApiError):
        client.access_token()


@pytest.mark.django_db
def test_access_token(mocker, first_agency):
    client = Client(first_agency)
    mock_response = mocker.Mock()
    mocker.patch.object(client, "_post", return_value=mock_response)
    mocker.patch("benefits.enrollment.api.AccessTokenResponse")

    token = client.access_token()

    assert token


@pytest.mark.django_db
def test_enroll_no_customer_token(first_agency):
    client = Client(first_agency)

    with pytest.raises(ValueError, match=r"customer_token"):
        client.enroll(None, "group_id")


@pytest.mark.django_db
def test_enroll_no_group_id(first_agency):
    client = Client(first_agency)

    with pytest.raises(ValueError, match=r"group_id"):
        client.enroll("customer_token", None)


@pytest.mark.django_db
def test_get_customer_no_token(first_agency):
    client = Client(first_agency)

    with pytest.raises(ValueError, match=r"token"):
        client._get_customer(None)


@pytest.mark.django_db
def test_get_customer_status_not_OK(mocker, first_agency):
    client = Client(first_agency)
    mock_response = mocker.Mock()
    mock_response.raise_for_status.side_effect = requests.HTTPError()
    mocker.patch.object(client, "_get", return_value=mock_response)

    with pytest.raises(ApiError):
        client._get_customer("token")


@pytest.mark.django_db
def test_get_customer_is_registered(mocker, first_agency):
    client = Client(first_agency)
    mock_get_response = mocker.Mock()
    mocker.patch.object(client, "_get", return_value=mock_get_response)

    mock_customer = mocker.Mock(spec=CustomerResponse)
    mock_customer.is_registered = True
    mocker.patch("benefits.enrollment.api.CustomerResponse", return_value=mock_customer)

    return_customer = client._get_customer("token")

    assert return_customer == mock_customer
    assert return_customer.is_registered


@pytest.mark.django_db
def test_get_customer_is_not_registered(mocker, first_agency):
    client = Client(first_agency)
    mock_get_response = mocker.Mock()
    mocker.patch.object(client, "_get", return_value=mock_get_response)

    mock_customer = mocker.Mock(spec=CustomerResponse)
    mock_customer.is_registered = False
    mock_customer.id = "id"
    mocker.patch("benefits.enrollment.api.CustomerResponse", return_value=mock_customer)

    update_spy = mocker.patch("benefits.enrollment.api.Client._update_customer")

    client._get_customer("token")

    update_spy.assert_called_once_with(mock_customer.id)


@pytest.mark.django_db
@pytest.mark.parametrize("exception", REQUESTS_ERRORS)
def test_get_customer_exception(mocker, first_agency, exception):
    client = Client(first_agency)
    mocker.patch.object(client, "_get", side_effect=exception)

    with pytest.raises(ApiError):
        client._get_customer("token")
