import requests

import pytest

from benefits.enrollment.api import ApiError, CustomerResponse, Client


REQUESTS_ERRORS = [requests.ConnectionError, requests.Timeout, requests.TooManyRedirects, requests.HTTPError]


@pytest.fixture
def api_client(first_agency):
    return Client(first_agency)


@pytest.fixture
def mocked_customer(mocker):
    mock = mocker.Mock(spec=CustomerResponse)
    mocker.patch("benefits.enrollment.api.CustomerResponse", return_value=mock)
    return mock


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
    assert isinstance(client.headers, dict)


@pytest.mark.django_db
def test_headers_none(api_client):
    headers = api_client._headers()

    assert headers == api_client.headers


@pytest.mark.django_db
def test_headers(api_client):
    headers = api_client._headers({"header": "value"})

    assert "header" in headers
    assert headers["header"] == "value"


@pytest.mark.django_db
def test_make_url(api_client):
    part1, part2, part3 = "part1", "part2", "part3"
    agency = api_client.agency

    url = api_client._make_url(part1, part2, part3)

    assert agency.payment_processor.api_base_url in url
    assert agency.merchant_id in url
    assert part1 in url
    assert part2 in url
    assert part3 in url


@pytest.mark.django_db
def test_get_customer_no_token(api_client):
    with pytest.raises(ValueError, match=r"token"):
        api_client._get_customer(None)


@pytest.mark.django_db
def test_get_customer_status_not_OK(mocker, api_client):
    mock_response = mocker.Mock()
    mock_response.raise_for_status.side_effect = requests.HTTPError()
    mocker.patch.object(api_client, "_get", return_value=mock_response)

    with pytest.raises(ApiError):
        api_client._get_customer("token")


@pytest.mark.django_db
def test_get_customer_is_registered(mocker, api_client, mocked_customer):
    mock_get_response = mocker.Mock()
    mocker.patch.object(api_client, "_get", return_value=mock_get_response)
    mocked_customer.is_registered = True

    return_customer = api_client._get_customer("token")

    assert return_customer == mocked_customer
    assert return_customer.is_registered


@pytest.mark.django_db
def test_get_customer_is_not_registered(mocker, api_client, mocked_customer):
    mock_get_response = mocker.Mock()
    mocker.patch.object(api_client, "_get", return_value=mock_get_response)
    mocked_customer.is_registered = False
    mocked_customer.id = "id"

    update_spy = mocker.patch("benefits.enrollment.api.Client._update_customer")

    api_client._get_customer("token")

    update_spy.assert_called_once_with(mocked_customer.id)


@pytest.mark.django_db
@pytest.mark.parametrize("exception", REQUESTS_ERRORS)
def test_get_customer_exception(mocker, api_client, exception):
    mocker.patch.object(api_client, "_get", side_effect=exception)

    with pytest.raises(ApiError):
        api_client._get_customer("token")


@pytest.mark.django_db
def test_update_customer_no_customer_id(api_client):
    with pytest.raises(ValueError):
        api_client._update_customer(None)


@pytest.mark.django_db
def test_update_customer(mocker, api_client, mocked_customer):
    mock_response = mocker.Mock()
    mocker.patch.object(api_client, "_patch", return_value=mock_response)

    updated_customer = api_client._update_customer("id")

    assert updated_customer == mocked_customer


@pytest.mark.django_db
@pytest.mark.parametrize("exception", REQUESTS_ERRORS)
def test_access_token_exception(mocker, api_client, exception):
    mock_response = mocker.Mock()
    mock_response.raise_for_status.side_effect = exception
    mocker.patch.object(api_client, "_post", return_value=mock_response)

    with pytest.raises(ApiError):
        api_client.access_token()


@pytest.mark.django_db
def test_access_token(mocker, api_client):
    mock_response = mocker.Mock()
    mocker.patch.object(api_client, "_post", return_value=mock_response)
    mocker.patch("benefits.enrollment.api.AccessTokenResponse")

    token = api_client.access_token()

    assert token


@pytest.mark.django_db
def test_enroll_no_customer_token(api_client):
    with pytest.raises(ValueError, match=r"customer_token"):
        api_client.enroll(None, "group_id")


@pytest.mark.django_db
def test_enroll_no_group_id(api_client):
    with pytest.raises(ValueError, match=r"group_id"):
        api_client.enroll("customer_token", None)
