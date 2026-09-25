import json

import pytest

from benefits.enrollment_init.api import Client


class TestClient:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = Client(api_url="https://example.com", username="api_user", password="api_password")

    def test_init(self):
        assert self.client.authorization_header_value == "Basic YXBpX3VzZXI6YXBpX3Bhc3N3b3Jk"

    def test_get_transit_account__returns_1(self, mocker):
        mock_response = mocker.Mock()
        mock_json = json.loads("""
        {
            "TotalCount": 1,
            "Result": [
                {
                    "Id": 1,
                    "Description": null,
                    "FareCategory": 1,
                    "FareCategoryExpiry": null,
                    "FareMediaId": "x",
                    "PrintedNumber": "411111~1111",
                    "ExternalIdentifier": null,
                    "SerialNumber": "x",
                    "CardTypeName": "EMV Card",
                    "FareMediaType": 217,
                    "State": 1,
                    "BlockingReason": 0,
                    "IsIssued": false,
                    "Balance": 0,
                    "PreTaxBalance": 0,
                    "TotalBalance": 0,
                    "CardholderId": null,
                    "CustomerAccountId": null,
                    "InstitutionAccountId": null,
                    "InstitutionAccountIds": [],
                    "Participants": [],
                    "ExpirationDate": "9999-12-31T23:59:59.999Z",
                    "FareMediaTypeExternalIdentifier": 10010,
                    "ParticipantId": null,
                    "SequentialNumber": null,
                    "BlockDate": null,
                    "HasVirtualCard": false,
                    "PrimaryAccountId": null,
                    "InventoryState": 1,
                    "HasPin": false,
                    "FareProductAssignmentId": [],
                    "AssociationType": null,
                    "AssociationDescription": null,
                    "ReplacedTransitAccountId": null,
                    "OrderDetailId": null,
                    "ReplacedTransitAccountPrintedCardNumber": null,
                    "PinCode": null,
                    "SecurityCode": null,
                    "PaymentAccountReference": null,
                    "ParticipantIdentifier": null,
                    "ParticipantFirstName": null,
                    "ParticipantLastName": null,
                    "ParticipantGroupName": null,
                    "ObservationStatus": null,
                    "Observation": null,
                    "CardHolderCustomAttributeValues": null,
                    "LastUsedDate": "2026-09-04T15:25:20.000Z",
                    "OpenLoopCardType": null,
                    "Imported": "2026-09-04T17:25:20Z"
                }
            ]
        }
        """)
        mock_response.json.return_value = mock_json
        mocker.patch("benefits.enrollment_init.api.requests.get", return_value=mock_response)

        response = self.client.get_transit_account("example card token")

        assert response.Id == 1
        assert response.CardholderId is None

    def test_get_transit_account__returns_0(self, mocker):
        mock_response = mocker.Mock()
        mock_json = json.loads("""
        {
            "TotalCount": 0,
            "Result": []
        }
        """)
        mock_response.json.return_value = mock_json
        mocker.patch("benefits.enrollment_init.api.requests.get", return_value=mock_response)

        response = self.client.get_transit_account("example card token")

        assert response is None

    def test_get_transit_account__returns_more_than_1(self, mocker):
        mock_response = mocker.Mock()
        mock_json = json.loads("""
        {
            "TotalCount": 2,
            "Result": [
                {
                    "Id": 1,
                    "Description": null,
                    "FareCategory": 1,
                    "FareCategoryExpiry": null,
                    "FareMediaId": "x",
                    "PrintedNumber": "411111~1111",
                    "ExternalIdentifier": null,
                    "SerialNumber": "x",
                    "CardTypeName": "EMV Card",
                    "FareMediaType": 217,
                    "State": 1,
                    "BlockingReason": 0,
                    "IsIssued": false,
                    "Balance": 0,
                    "PreTaxBalance": 0,
                    "TotalBalance": 0,
                    "CardholderId": null,
                    "CustomerAccountId": null,
                    "InstitutionAccountId": null,
                    "InstitutionAccountIds": [],
                    "Participants": [],
                    "ExpirationDate": "9999-12-31T23:59:59.999Z",
                    "FareMediaTypeExternalIdentifier": 10010,
                    "ParticipantId": null,
                    "SequentialNumber": null,
                    "BlockDate": null,
                    "HasVirtualCard": false,
                    "PrimaryAccountId": null,
                    "InventoryState": 1,
                    "HasPin": false,
                    "FareProductAssignmentId": [],
                    "AssociationType": null,
                    "AssociationDescription": null,
                    "ReplacedTransitAccountId": null,
                    "OrderDetailId": null,
                    "ReplacedTransitAccountPrintedCardNumber": null,
                    "PinCode": null,
                    "SecurityCode": null,
                    "PaymentAccountReference": null,
                    "ParticipantIdentifier": null,
                    "ParticipantFirstName": null,
                    "ParticipantLastName": null,
                    "ParticipantGroupName": null,
                    "ObservationStatus": null,
                    "Observation": null,
                    "CardHolderCustomAttributeValues": null,
                    "LastUsedDate": "2026-09-04T15:25:20.000Z",
                    "OpenLoopCardType": null,
                    "Imported": "2026-09-04T17:25:20Z"
                },
                {
                    "Id": 2,
                    "Description": null,
                    "FareCategory": 1,
                    "FareCategoryExpiry": null,
                    "FareMediaId": "x",
                    "PrintedNumber": "411111~1111",
                    "ExternalIdentifier": null,
                    "SerialNumber": "x",
                    "CardTypeName": "EMV Card",
                    "FareMediaType": 217,
                    "State": 1,
                    "BlockingReason": 0,
                    "IsIssued": false,
                    "Balance": 0,
                    "PreTaxBalance": 0,
                    "TotalBalance": 0,
                    "CardholderId": null,
                    "CustomerAccountId": null,
                    "InstitutionAccountId": null,
                    "InstitutionAccountIds": [],
                    "Participants": [],
                    "ExpirationDate": "9999-12-31T23:59:59.999Z",
                    "FareMediaTypeExternalIdentifier": 10010,
                    "ParticipantId": null,
                    "SequentialNumber": null,
                    "BlockDate": null,
                    "HasVirtualCard": false,
                    "PrimaryAccountId": null,
                    "InventoryState": 1,
                    "HasPin": false,
                    "FareProductAssignmentId": [],
                    "AssociationType": null,
                    "AssociationDescription": null,
                    "ReplacedTransitAccountId": null,
                    "OrderDetailId": null,
                    "ReplacedTransitAccountPrintedCardNumber": null,
                    "PinCode": null,
                    "SecurityCode": null,
                    "PaymentAccountReference": null,
                    "ParticipantIdentifier": null,
                    "ParticipantFirstName": null,
                    "ParticipantLastName": null,
                    "ParticipantGroupName": null,
                    "ObservationStatus": null,
                    "Observation": null,
                    "CardHolderCustomAttributeValues": null,
                    "LastUsedDate": "2026-09-04T15:25:20.000Z",
                    "OpenLoopCardType": null,
                    "Imported": "2026-09-04T17:25:20Z"
                }
            ]
        }
        """)
        mock_response.json.return_value = mock_json
        mocker.patch("benefits.enrollment_init.api.requests.get", return_value=mock_response)

        card_token = "example card token"
        with pytest.raises(ValueError, match=f"Unexpectedly received more than 1 TransitAccount for token {card_token}"):
            self.client.get_transit_account(card_token)

    def test_get_cardholder_returns_1(self, mocker):
        mock_response = mocker.Mock()

        mock_json = json.loads("""
        {
            "Id": 12002,
            "FirstName": "",
            "MiddleName": "",
            "LastName": "",
            "PhoneNumber": "",
            "DateOfBirth": "0001-01-01T00:00:00.000Z",
            "Email": "",
            "CellPhoneNumber": "",
            "FaxNumber": "",
            "Gender": 0,
            "Identifier": "",
            "FareCategory": 7,
            "FareCategoryExpiry": null,
            "AddressId": null,
            "TransitAccountId": 17718,
            "HasImage": false,
            "InstitutionAccountId": null,
            "PersonalCareAssistant": false,
            "Address": null,
            "OrderDetailId": null,
            "CardPrintedNumber": null
            }
        """)
        mock_response.json.return_value = mock_json
        mocker.patch("benefits.enrollment_init.api.requests.get", return_value=mock_response)

        response = self.client.get_cardholder(12002)

        assert response.FareCategory == 7
        assert response.FareCategoryExpiry is None

    def test_get_cardholder_returns_0(self, mocker):
        mock_response = mocker.Mock()

        # MOBILEvario API returns this JSON as the response if no cardholder found
        mock_json = json.loads("""
        {"HttpStatus":404,"Errors":[{"ErrorCode":33685548,"Message":"Invalid card holder.","ParameterName":"cardholderId"}]}
        """)

        mock_response.json.return_value = mock_json
        mocker.patch("benefits.enrollment_init.api.requests.get", return_value=mock_response)

        response = self.client.get_cardholder(11111)

        assert response is None

    def test_get_cardholder_returns_unexpected_http_status(self, mocker):
        mock_response = mocker.Mock()

        mock_json = json.loads("""
        {"HttpStatus":500}
        """)

        mock_response.json.return_value = mock_json
        mocker.patch("benefits.enrollment_init.api.requests.get", return_value=mock_response)

        cardholder_id = 111111
        with pytest.raises(ValueError, match=f"Unexpected response when querying for cardholder {cardholder_id}: {mock_json}"):
            self.client.get_cardholder(cardholder_id)

    def test_post_cardholder(self, mocker):
        mock_response = mocker.Mock()
        mock_json = json.loads("""
        {
            "Id": 1,
            "FirstName": "sample string 2",
            "MiddleName": "sample string 3",
            "LastName": "sample string 4",
            "PhoneNumber": "sample string 5",
            "DateOfBirth": "2026-09-25T20:03:41.386Z",
            "Email": "sample string 7",
            "CellPhoneNumber": "sample string 8",
            "FaxNumber": "sample string 9",
            "Gender": 0,
            "Identifier": "sample string 10",
            "FareCategory": 1,
            "FareCategoryExpiry": null,
            "AddressId": 1,
            "TransitAccountId": 1,
            "HasImage": true,
            "InstitutionAccountId": 1,
            "PersonalCareAssistant": true,
            "Address": {
                "Id": 1,
                "AddressLine1": "sample string 2",
                "AddressLine2": "sample string 3",
                "PostalCode": "sample string 4",
                "City": "sample string 5",
                "State": "sample string 6",
                "Country": "sample string 7",
                "Description": "sample string 8",
                "Addressee": "sample string 9"
            },
            "OrderDetailId": 1,
            "CardPrintedNumber": "sample string 13"
        }
        """)
        mock_response.json.return_value = mock_json
        mocker.patch("benefits.enrollment_init.api.requests.post", return_value=mock_response)

        response = self.client.post_cardholder(fare_category=1, transit_account_id=1)

        assert response.FareCategory == 1
        assert response.FareCategoryExpiry is None
