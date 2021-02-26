"""
The discounts application: Discounts API implementation.
"""
import tempfile
import time
import uuid

import requests

from benefits.core.api import Response


class Client:
    """Base Provider API client. Dot not use this class directly. Use one of the child class implementations."""

    def __init__(self, agency):
        self.agency = agency
        self.provider = agency.discount_provider
        self.headers = {"Accept": "application/json", "Content-type": "application/json"}

    def _headers(self, headers=None):
        h = dict(self.headers)
        if headers:
            h.update(headers)
        return h

    def _get(self, url, payload, headers=None):
        h = self._headers(headers)
        return self._cert_request(lambda verify, cert: requests.get(url, headers=h, params=payload, verify=verify, cert=cert))

    def _patch(self, url, payload, headers=None):
        h = self._headers(headers)
        return self._cert_request(lambda verify, cert: requests.patch(url, headers=h, json=payload, verify=verify, cert=cert))

    def _post(self, url, payload, headers=None):
        h = self._headers(headers)
        return self._cert_request(lambda verify, cert: requests.post(url, headers=h, json=payload, verify=verify, cert=cert))

    def _cert_request(self, request_func):
        """
        Creates named (on-disk) temp files for client cert auth.
        * request_func: parameterized callable from `requests` library (e.g. `requests.get`).
        """
        # requests library reads temp files from file path
        # The "with" context destroys temp files when response comes back
        with tempfile.NamedTemporaryFile("w+") as cert, tempfile.NamedTemporaryFile("w+") as key, tempfile.NamedTemporaryFile(
            "w+"
        ) as ca:

            cert.write(self.provider.client_cert_pem)
            cert.seek(0)

            key.write(self.provider.client_cert_private_key_pem)
            key.seek(0)

            ca.write(self.provider.client_cert_root_ca_pem)
            ca.seek(0)

            # request using temp file paths
            return request_func(verify=ca.name, cert=(cert.name, key.name))


class AccessTokenResponse(Response):
    """Discount Provider API Access Token response."""

    def __init__(self, response, agency, provider):
        super().__init__(response.status_code)

        # bail early for remote server errors
        if self.status_code >= 500:
            return

        # read response payload from body
        try:
            payload = response.json()
        except ValueError as ex:
            self._assign_error(ex, "Invalid response format")
            return

        # extract the token data
        self.access_token = payload.get("access_token")
        self.token_type = payload.get("token_type")
        self.expires_in = payload.get("expires_in")
        if self.expires_in is not None:
            self.expiry = time.time() + self.expires_in
        else:
            self.expiry = None


class AccessTokenClient(Client):
    """Discounts Provider API Access Token client."""

    def get(self):
        """Obtain an access token to use for integrating with other APIs."""

        url = "/".join((self.provider.api_base_url, self.agency.merchant_id, self.provider.api_access_token_endpoint))

        payload = {self.provider.api_access_token_request_key: self.provider.api_access_token_request_val}

        try:
            r = self._post(url, payload)
        except requests.ConnectionError as ex:
            return Response(500, error=ex, message="Access token: Connection to discounts server failed")
        except requests.Timeout as ex:
            return Response(500, error=ex, message="Access token: Connection to discounts server timed out")
        except requests.TooManyRedirects as ex:
            return Response(500, error=ex, message="Access token: Too many redirects to discounts server")
        except Exception as ex:
            return Response(500, error=ex, message="Access token: Error")

        if r.status_code in (200, 201):
            return AccessTokenResponse(r, self.agency, self.provider)
        elif r.status_code == 400:
            return Response(r.status_code, message="Access token: Bad request payload")
        elif r.status_code == 404:
            return Response(r.status_code, message="Access token: Not found")
        else:
            return Response(r.status_code, message="Access token: Error")


class CustomerResponse(Response):
    """Discount Provider Customer API response."""

    def __init__(self, response):
        super().__init__(response.status_code)

        # bail early for remote server errors
        if self.status_code >= 500:
            return

        # read response payload from body
        try:
            payload = response.json()
        except ValueError as ex:
            self._assign_error(ex, "Invalid response format")
            return

        # extract the customer data
        self.id = payload.get("id")
        self.customer_ref = payload.get("customer_ref")
        self.is_registered = payload.get("is_registered")
        self.created_date = payload.get("created_date")


class CustomerClient(Client):
    """Discounts Provider Customer API client."""

    def create_or_update(self, token):
        """Create or update a customer in the Discount Provider's system using the token that represents that customer."""
        url = "/".join((self.provider.api_base_url, self.agency.merchant_id, self.provider.customers_endpoint))

        payload = {"token": token}

        try:
            r = self._get(url, payload)
            if r.status_code == 200:
                # customer already exists with this token, update registration with ref
                customer = CustomerResponse(r)
                return self._update(customer)
            elif r.status_code == 404:
                # customer does not exist with this token, create customer
                return self._create(payload)
            else:
                return Response(r.status_code, message="Customer: Error")
        except requests.ConnectionError as ex:
            return Response(500, error=ex, message="Customer: Connection to discounts server failed")
        except requests.Timeout as ex:
            return Response(500, error=ex, message="Customer: Connection to discounts server timed out")
        except requests.TooManyRedirects as ex:
            return Response(500, error=ex, message="Customer: Too many redirects to discounts server")
        except Exception as ex:
            return Response(500, error=ex, message="Customer: Error")

    def _create(self, payload):
        """Create the customer represented by the payload token."""
        url = "/".join((self.provider.api_base_url, self.agency.merchant_id, self.provider.customers_endpoint))

        payload.update({"customer_ref": uuid.uuid4(), "is_registered": True})

        r = self._post(url, payload)

        if r.status_code in (200, 201):
            return CustomerResponse(r)
        elif r.status_code == 400:
            return Response(r.status_code, message="Customer: Bad create payload")
        elif r.status_code == 404:
            return Response(r.status_code, message="Customer: Invalid token")
        elif r.status_code == 409:
            return Response(r.status_code, message="Customer: Customer with token or ref already exists")
        else:
            return Response(r.status_code, message="Customer: Error")

    def _update(self, customer):
        """Update the customer represented by the CustomerResponse object."""
        url = "/".join((self.provider.api_base_url, self.agency.merchant_id, self.provider.customer_endpoint, customer.id))

        payload = {"customer_ref": customer.customer_ref or uuid.uuid4(), "is_registered": True}

        r = self._patch(url, payload)

        if r.status_code in (200, 201):
            return CustomerResponse(r)
        elif r.status_code == 400:
            return Response(r.status_code, message="Customer: Bad update payload")
        elif r.status_code == 404:
            return Response(r.status_code, message="Customer: Customer not found")
        elif r.status_code == 409:
            return Response(r.status_code, message="Customer: Customer with ref already exists, or ref mismatch")
        else:
            return Response(r.status_code, message="Customer: Error")


class GroupResponse(Response):
    """Discount Provider Customer Group API response."""

    def __init__(self, response, payload=None):
        super().__init__(response.status_code)

        if payload is None:
            # read response payload from body
            try:
                payload = response.json()
            except ValueError as ex:
                self._assign_error(ex, "Invalid response format")
                return

        # extract the customer data
        self.customer_ids = payload.get("customer_ids", [])
        self.updated_count = len(self.customer_ids)
        self.updated_customer_id = self.customer_ids[0] if self.updated_count == 1 else None


class GroupClient(Client):
    """Discounts Provider Customer Group API client."""

    def enroll_customer(self, customer_id, group_id):
        """Enroll the customer in the group."""
        url = "/".join((self.provider.api_base_url, self.agency.merchant_id, self.provider.groups_endpoint, group_id))

        payload = {"customer_ids": [customer_id]}

        try:
            r = self._patch(url, payload)

            if r.status_code in (200, 201):
                return GroupResponse(r)
            elif r.status_code == 403:
                return Response(r.status_code, message="Group: Invalid merchant_id")
            elif r.status_code == 500:
                # 500 indicates the customer already exists in the group
                return GroupResponse(r, payload=payload)
            else:
                return Response(r.status_code, message="Group: Error")
        except requests.ConnectionError as ex:
            return Response(500, error=ex, message="Group: Connection to discounts server failed")
        except requests.Timeout as ex:
            return Response(500, error=ex, message="Group: Connection to discounts server timed out")
        except requests.TooManyRedirects as ex:
            return Response(500, error=ex, message="Group: Too many redirects to discounts server")
        except Exception as ex:
            return Response(500, error=ex, message="Group: Error")
