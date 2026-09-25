import base64
from dataclasses import dataclass

import requests

from benefits.enrollment_switchio.api import BaseDataClass


@dataclass
class TransitAccountResponse(BaseDataClass):
    Id: int
    CardholderId: int


@dataclass
class CardholderResponse(BaseDataClass):
    FareCategory: int
    FareCategoryExpiry: str


class Client:
    def __init__(self, api_url, username, password):
        self.api_url = api_url.strip("/")

        encoded_bytes = base64.b64encode(bytes(f"{username}:{password}", "utf-8"))
        self.authorization_header_value = f"Basic {encoded_bytes.decode()}"

    def _endpoint_url(self, endpoint):
        return f"{self.api_url}/api/{endpoint}"

    def _authorization_header(self):
        return {"Authorization": self.authorization_header_value}

    def get_transit_account(self, banking_service_token, timeout=5) -> TransitAccountResponse:
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

    def get_cardholder(self, cardholder_id: int, timeout=5) -> CardholderResponse:
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

    def post_cardholder(self, fare_category: int, transit_account_id: int, timeout=5) -> CardholderResponse:
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
