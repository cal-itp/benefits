import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import pytest
from django.utils import timezone as tz

import benefits.enrollment_switchio.api
from benefits.enrollment_switchio.api import (
    BaseDataClass,
    Client,
    EnrollmentClient,
    EshopResponseMode,
    Group,
    GroupExpiry,
    Registration,
    RegistrationMode,
    RegistrationStatus,
    TokenizationClient,
)


class TestBaseDataClass:

    @dataclass
    class SampleDataClass(BaseDataClass):
        fieldOne: int
        fieldTwo: str

    def test_from_kwargs(self, caplog):
        response_json = {"fieldOne": 1, "fieldTwo": "two", "fieldThree": "three"}

        with caplog.at_level(logging.DEBUG):
            instance = self.SampleDataClass.from_kwargs(**response_json)

        assert instance.fieldOne == 1
        assert instance.fieldTwo == "two"
        assert f"Unexpected arg parsing response for {self.SampleDataClass}: fieldThree = three" in caplog.text


class TestRegistration:
    def test_unexpected_fields(self):
        response_json = {"regId": "1234", "gtwUrl": "https://example.com", "unexpectedField": "value"}

        # this test will fail if any error occurs from instantiating the class
        Registration.from_kwargs(**response_json)


class TestRegistrationStatus:
    def test_unexpected_fields(self):
        response_json = {
            "regState": "state",
            "created": datetime(2026, 8, 24, 11, 30, 0),
            "mode": RegistrationMode.REGISTER,
            "tokens": [{"token": "1234"}],
            "eshopResponseMode": EshopResponseMode.FORM_POST,
            "identType": "ident",
            "maskCln": "cln",
            "cardExp": "08/26",
            "unexpectedField": "value",
        }

        # this test will fail if any error occurs from instantiating the class
        RegistrationStatus.from_kwargs(**response_json)


@pytest.mark.django_db
class TestClient:
    def test_cert_request(self, mocker):
        temp_file = mocker.patch("benefits.enrollment_switchio.api.NamedTemporaryFile")
        request_func = mocker.Mock()

        client = Client(
            private_key="private key contents",
            client_certificate="client cert contents",
            ca_certificate="ca cert contents",
        )
        client._cert_request(request_func)

        temp_file.assert_called()
        request_func.assert_called_once()
        assert "verify" in request_func.call_args.kwargs
        assert "cert" in request_func.call_args.kwargs


class TestTokenizationClient:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.tokenization_client = TokenizationClient(
            api_url="https://example.com",
            api_key="api key",
            api_secret="api secret",
            private_key="private key contents",
            client_certificate="client cert contents",
            ca_certificate="ca cert contents",
        )

    @pytest.mark.parametrize("method", ["GET", "POST"])
    @pytest.mark.parametrize("body", ['{"exampleProperty": "blah"}', None, ""])
    def test_signature_input_string(self, method, body):
        timestamp = str(int(datetime.now().timestamp()))
        request_path = "/api/example"

        input_string = self.tokenization_client._signature_input_string(
            timestamp=timestamp, method=method, request_path=request_path, body=body
        )

        if body is None:
            expected = f"{timestamp}{method}{request_path}"
        else:
            expected = f"{timestamp}{method}{request_path}{body}"

        assert input_string == expected

    def test_stp_signature(self):
        timestamp = "1748637999"
        method = "GET"
        request_path = "/api/example"
        body = '{"exampleProperty": "blah"}'

        stp_signature = self.tokenization_client._stp_signature(
            timestamp=timestamp, method=method, request_path=request_path, body=body
        )

        # the expected STP-SIGNATURE value based on those inputs
        expected = "7da3dd8dad6af77d4f0d5b96ff250399f2ffe1dac2fdfbdbfae0c22a86366426"

        assert stp_signature == expected

    @pytest.mark.parametrize("method", ["GET", "POST"])
    @pytest.mark.parametrize("body", [{"exampleProperty": "blah"}, None])
    def test_get_headers(self, mocker, method, body):
        timestamp = 1516867520

        # mock datetime.now()
        datetime_mock = mocker.Mock()
        datetime_mock.now.return_value = datetime.fromtimestamp(timestamp)
        mocker.patch.object(benefits.enrollment_switchio.api, "datetime", datetime_mock)

        request_path = "/api/example"

        headers = self.tokenization_client._get_headers(method=method, request_path=request_path, request_body=body)

        # calculate the expected value
        timestamp = str(timestamp)
        expected = {
            "STP-APIKEY": self.tokenization_client.api_key,
            "STP-TIMESTAMP": timestamp,
            "STP-SIGNATURE": self.tokenization_client._stp_signature(
                timestamp=timestamp,
                method=method,
                request_path=request_path,
                body=json.dumps(body) if body else None,
            ),
        }

        assert headers == expected

    def test_request_registration(self, mocker):
        mock_response = mocker.Mock()
        mock_json = dict(regId="1234", gtwUrl="https://example.com/cst/?regId=1234")
        mock_response.json.return_value = mock_json
        mocker.patch("benefits.enrollment_switchio.api.TokenizationClient._cert_request", return_value=mock_response)

        registration = self.tokenization_client.request_registration(
            eshopRedirectUrl="https://localhost/enrollment",
            mode=RegistrationMode.REGISTER,
            eshopResponseMode=EshopResponseMode.FORM_POST,
        )

        assert registration == Registration(**mock_json)

    def test_get_registration_status(self, mocker):
        mock_response = mocker.Mock()
        mock_json = dict(
            regState="created",
            created="2025-05-28T18:26:03.353",
            mode="register",
            tokens=[],
            eshopResponseMode="form_post",
            identType="BPK",
            maskCln="412501****1234",
            cardExp="1119",
        )
        mock_response.json.return_value = mock_json
        mocker.patch("benefits.enrollment_switchio.api.TokenizationClient._cert_request", return_value=mock_response)

        registration_status = self.tokenization_client.get_registration_status(registration_id="1234")

        assert registration_status == RegistrationStatus(**mock_json)


class TestGroup:
    def test_unexpected_fields(self):
        response_json = {
            "id": 1,
            "operatorId": 1,
            "name": "Group 1",
            "code": "group",
            "value": 1,
            "unexpectedField": "value",
        }

        # this test will fail if any error occurs from instantiating the class
        Group.from_kwargs(**response_json)


class TestGroupExpiry:
    def test_expiresAt(self):
        group = GroupExpiry(group="group", expiresAt="2025-09-12T00:00:00Z")

        assert group.expiresAt == datetime(2025, 9, 12, 0, 0, 0, tzinfo=timezone.utc)

    def test_no_expiresAt(self):
        group = GroupExpiry(group="group", expiresAt=None)

        assert group.expiresAt is None

    def test_unexpected_fields(self):
        response_json = {"group": "group", "expiresAt": "2025-09-12T00:00:00Z", "unexpectedField": "value"}

        # this test will fail if any error occurs from instantiating the class
        GroupExpiry.from_kwargs(**response_json)


class TestEnrollmentClient:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.enrollment_client = EnrollmentClient(
            api_url="https://example.com",
            authorization_header_value="Basic abc123",
            private_key="private key contents",
            client_certificate="client cert contents",
            ca_certificate="ca cert contents",
        )

    @pytest.mark.parametrize(
        "expiry_datetime",
        [
            datetime(2025, 9, 12, 19, 15, 0, tzinfo=timezone.utc),
            datetime(2025, 9, 12, 19, 15, 0, tzinfo=None),
            datetime(2025, 9, 12, 12, 15, 0, tzinfo=tz.get_fixed_timezone(timedelta(hours=-7))),
        ],
    )
    def test_format_expiry(self, expiry_datetime):
        expected_format = "2025-09-12T19:15:00Z"
        formatted = self.enrollment_client._format_expiry(expiry_datetime)

        assert formatted == expected_format

    def test_get_headers(self):
        headers = self.enrollment_client._get_headers()

        assert headers == {"Authorization": "Basic abc123"}

    def test_healthcheck(self, mocker):
        mock_response = mocker.Mock()
        mock_response.text.return_value = "Egibility is alive!"
        mocker.patch("benefits.enrollment_switchio.api.EnrollmentClient._cert_request", return_value=mock_response)

        response = self.enrollment_client.healthcheck()

        assert response == mock_response.text

    def test_get_groups(self, mocker):
        mock_response = mocker.Mock()
        mock_json = dict(
            id=1,
            operatorId=123,
            name="Veteran Discount",
            code="veteran-discount",
            value=10,
        )
        mock_response.json.return_value = [mock_json]
        mocker.patch("benefits.enrollment_switchio.api.EnrollmentClient._cert_request", return_value=mock_response)

        groups = self.enrollment_client.get_groups(pto_id="123")

        assert groups == [Group(**mock_json)]

    def test_get_groups_for_token(self, mocker):
        mock_response = mocker.Mock()
        mock_json = dict(group="veteran-discount", expiresAt=None)
        mock_response.json.return_value = [mock_json]
        mocker.patch("benefits.enrollment_switchio.api.EnrollmentClient._cert_request", return_value=mock_response)

        groups = self.enrollment_client.get_groups_for_token(pto_id="123", token="abcde12345")

        assert groups == [GroupExpiry(**mock_json)]

    @pytest.mark.parametrize(
        "expiry, expected_expires_at",
        [
            (None, None),
            (datetime(2025, 9, 12, 19, 15, 0, tzinfo=timezone.utc), "2025-09-12T19:15:00Z"),
        ],
    )
    def test_add_group_to_token(self, mocker, expiry, expected_expires_at):
        mock_post = mocker.patch("benefits.enrollment_switchio.api.requests.post")

        def cert_request_spy(request_func):
            # the original `_cert_request` adds `verify` and `cert` kwargs.
            # pass dummy values here to satisfy the lambda's signature.
            return request_func(verify="dummy_ca_path", cert=("dummy_cert_path", "dummy_key_path"))

        mocker.patch.object(self.enrollment_client, "_cert_request", side_effect=cert_request_spy)

        pto_id = "123"
        group_id = "test-group"
        token = "test-token"

        self.enrollment_client.add_group_to_token(pto_id, group_id, token, expiry=expiry)

        expected_body = {"group": group_id}
        if expected_expires_at:
            expected_body["expiresAt"] = expected_expires_at

        # Assert that `requests.post` was called with the correct URL and body.
        expected_url = f"{self.enrollment_client.api_url}/api/external/discount/{pto_id}/token/{token}/add"
        mock_post.assert_called_once()
        assert mock_post.call_args.args == (expected_url,)
        assert mock_post.call_args.kwargs["json"] == expected_body

    def test_remove_group_from_token(self, mocker):
        group_code = "veteran-discount"
        token = "abcde12345"

        mock_response = mocker.Mock()
        mock_response.text.return_value = f"Discount {group_code} removed successfully for token {token}"
        mocker.patch("benefits.enrollment_switchio.api.EnrollmentClient._cert_request", return_value=mock_response)

        response = self.enrollment_client.remove_group_from_token("123", group_code, token)

        assert response == mock_response.text
