import base64
from dataclasses import asdict, dataclass
from datetime import datetime

import requests
from django.conf import settings

from benefits.enrollment.api import BaseDataClass


@dataclass
class TransitAccountResponse(BaseDataClass):
    Id: int
    CardholderId: int


@dataclass
class CardholderUpdateModel(BaseDataClass):
    """
    Represents the body parameters that can be sent when updating a Cardholder.
    """

    FirstName: str | None = None
    MiddleName: str | None = None
    LastName: str | None = None
    PhoneNumber: str | None = None
    DateOfBirth: str | None = None
    Email: str | None = None
    CellPhoneNumber: str | None = None
    FaxNumber: str | None = None
    Gender: str | None = None
    Identifier: str | None = None
    FareCategory: int | None = None
    FareCategoryExpiry: datetime | None = None
    TransitAccountId: int | None = None
    PersonalCareAssistant: bool | None = None


@dataclass
class CardholderResponse(BaseDataClass):
    FirstName: str | None = None
    MiddleName: str | None = None
    LastName: str | None = None
    PhoneNumber: str | None = None
    DateOfBirth: str | None = None
    Email: str | None = None
    CellPhoneNumber: str | None = None
    FaxNumber: str | None = None
    Gender: str | None = None
    Identifier: str | None = None
    FareCategory: int | None = None
    FareCategoryExpiry: datetime | None = None
    TransitAccountId: int | None = None
    PersonalCareAssistant: bool | None = None
    # there are more fields that can be returned, but we don't need them and they're not in the PUT parameters

    def __post_init__(self):
        """Parses any date parameters into aware Python datetime objects.

        For @dataclasses with a generated __init__ function, this function is called automatically.

        https://docs.python.org/3.12/library/datetime.html#datetime.datetime.fromisoformat
        """
        if self.FareCategoryExpiry:
            self.FareCategoryExpiry = datetime.fromisoformat(self.FareCategoryExpiry)


class Client:
    def __init__(self, api_url, username, password):
        self.api_url = api_url.strip("/")

        encoded_bytes = base64.b64encode(bytes(f"{username}:{password}", "utf-8"))
        self.authorization_header_value = f"Basic {encoded_bytes.decode()}"

    def _endpoint_url(self, endpoint):
        return f"{self.api_url}/api/{endpoint}"

    def _authorization_header(self):
        return {"Authorization": self.authorization_header_value}

    def get_transit_account(self, banking_service_token, timeout=settings.REQUESTS_TIMEOUT) -> TransitAccountResponse:
        url = self._endpoint_url("TransitAccounts")
        response = requests.get(
            url,
            params={
                "BankingServiceToken": banking_service_token,
            },
            headers=self._authorization_header(),
            timeout=timeout,
        )

        response.raise_for_status()

        response_json = response.json()
        total_count = response_json["TotalCount"]
        results = response_json["Result"]

        if total_count == 1:
            return TransitAccountResponse.from_kwargs(**results[0])
        elif total_count == 0:
            return None
        else:
            raise ValueError(f"Unexpectedly received more than 1 TransitAccount for token {banking_service_token}")

    def get_cardholder(self, cardholder_id: int, timeout=settings.REQUESTS_TIMEOUT) -> CardholderResponse:
        url = self._endpoint_url("Cardholders") + f"/{cardholder_id}"
        response = requests.get(
            url,
            headers=self._authorization_header(),
            timeout=timeout,
        )

        response.raise_for_status()

        response_json = response.json()

        if "Id" in response_json and response_json["Id"] == cardholder_id:
            return CardholderResponse.from_kwargs(**response_json)
        else:
            raise ValueError(f"Unexpected response when querying for cardholder {cardholder_id}: {response_json}")

    def post_cardholder(
        self, fare_category: int, transit_account_id: int, timeout=settings.REQUESTS_TIMEOUT
    ) -> CardholderResponse:
        url = self._endpoint_url("Cardholders")
        request_body = {
            "FareCategory": fare_category,
            "TransitAccountId": transit_account_id,
        }
        response = requests.post(
            url,
            json=request_body,
            headers=self._authorization_header(),
            timeout=timeout,
        )

        response.raise_for_status()

        return CardholderResponse.from_kwargs(**response.json())

    def put_cardholder(
        self, cardholder_id: int, cardholder_update_model: CardholderUpdateModel, timeout=settings.REQUESTS_TIMEOUT
    ) -> CardholderResponse:
        url = self._endpoint_url("Cardholders") + f"/{cardholder_id}"
        request_body = asdict(cardholder_update_model)
        response = requests.put(
            url,
            json=request_body,
            headers=self._authorization_header(),
            timeout=timeout,
        )

        response.raise_for_status()

        return CardholderResponse.from_kwargs(**response.json())
