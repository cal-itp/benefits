"""
The discounts application: Discounts API implementation.
"""
import logging
from tempfile import NamedTemporaryFile
import time
import uuid

import requests


logger = logging.getLogger(__name__)


class Client:
    """Base Discount Provider API client. Dot not use this class directly. Use one of the child class implementations."""

    def __init__(self, agency):
        logger.debug("Initialize base Discount Provider API Client")

        if agency is None:
            raise ValueError("agency")
        if agency.discount_provider is None:
            raise ValueError("agency.discount_provider")

        self.agency = agency
        self.provider = agency.discount_provider
        self.headers = {"Accept": "application/json", "Content-type": "application/json"}

    def _headers(self, headers=None):
        h = dict(self.headers)
        if headers:
            h.update(headers)
        return h

    def _get(self, url, payload, headers=None):
        logger.debug("GET request in base Discount Provider API Client")
        h = self._headers(headers)
        return self._cert_request(lambda verify, cert: requests.get(url, headers=h, params=payload, verify=verify, cert=cert))

    def _patch(self, url, payload, headers=None):
        logger.debug("PATCH request in base Discount Provider API Client")
        h = self._headers(headers)
        return self._cert_request(lambda verify, cert: requests.patch(url, headers=h, json=payload, verify=verify, cert=cert))

    def _post(self, url, payload, headers=None):
        logger.debug("POST request in base Discount Provider API Client")
        h = self._headers(headers)
        return self._cert_request(lambda verify, cert: requests.post(url, headers=h, json=payload, verify=verify, cert=cert))

    def _cert_request(self, request_func):
        """
        Creates named (on-disk) temp files for client cert auth.
        * request_func: curried callable from `requests` library (e.g. `requests.get`).
        """
        # requests library reads temp files from file path
        # The "with" context destroys temp files when response comes back
        with NamedTemporaryFile("w+") as cert, NamedTemporaryFile("w+") as key, NamedTemporaryFile("w+") as ca:
            # write provider client cert data to temp files
            # resetting so they can be read again by requests
            cert.write(self.provider.client_cert_pem)
            cert.seek(0)

            key.write(self.provider.client_cert_private_key_pem)
            key.seek(0)

            ca.write(self.provider.client_cert_root_ca_pem)
            ca.seek(0)

            # request using temp file paths
            return request_func(verify=ca.name, cert=(cert.name, key.name))


class AccessTokenError(Exception):
    """Error with Discounts API access token."""

    pass


class AccessTokenResponse:
    """Discount Provider API Access Token response."""

    def __init__(self, response):
        logger.info("Read access token from response")

        try:
            payload = response.json()
        except ValueError:
            raise AccessTokenError("Invalid response format")

        self.access_token = payload.get("access_token")
        self.token_type = payload.get("token_type")
        self.expires_in = payload.get("expires_in")
        if self.expires_in is not None:
            logger.debug("Access token has expiry")
            self.expiry = time.time() + self.expires_in
        else:
            logger.debug("Access token has no expiry")
            self.expiry = None

        logger.info("Access token successfully read from response")


class AccessTokenClient(Client):
    """Discounts Provider API Access Token client."""

    def get(self):
        """Obtain an access token to use for integrating with other APIs."""
        logger.info("Get new access token")

        url = "/".join((self.provider.api_base_url, self.agency.merchant_id, self.provider.api_access_token_endpoint))
        payload = {self.provider.api_access_token_request_key: self.provider.api_access_token_request_val}

        try:
            r = self._post(url, payload)
            r.raise_for_status()
        except requests.ConnectionError:
            raise AccessTokenError("Connection to discounts server failed")
        except requests.Timeout:
            raise AccessTokenError("Connection to discounts server timed out")
        except requests.TooManyRedirects:
            raise AccessTokenError("Too many redirects to discounts server")
        except requests.HTTPError as e:
            raise AccessTokenError(e)

        return AccessTokenResponse(r)


class CustomerApiError(Exception):
    """Error calling Customer API."""

    pass


class CustomerResponse:
    """Discount Provider Customer API response."""

    def __init__(self, response, customer_id=None):
        logger.info("Read customer details from response")

        try:
            payload = response.json()
        except ValueError:
            raise CustomerApiError("Invalid response format")

        self.id = payload.get("id", customer_id)
        self.customer_ref = payload.get("customer_ref")
        self.is_registered = str(payload.get("is_registered", "false")).lower() == "true"

        logger.info("Customer details successfully read from response")


class CustomerClient(Client):
    """Discounts Provider Customer API client."""

    def create_or_update(self, token):
        """Create or update a customer in the Discount Provider's system using the token that represents that customer."""
        logger.info("Check for existing customer record")

        if token is None:
            raise ValueError("token")

        url = "/".join((self.provider.api_base_url, self.agency.merchant_id, self.provider.customers_endpoint))
        payload = {"token": token}

        try:
            r = self._get(url, payload)
            if r.status_code == 200:
                logger.debug("Customer record exists")
                customer = CustomerResponse(r)
                if customer.is_registered:
                    logger.debug("Customer is registered, skip update")
                    return customer
                else:
                    logger.debug("Customer is not registered, update")
                    return self._update(customer.id, customer.customer_ref)
            elif r.status_code == 404:
                logger.debug("Customer does not exist, create")
                return self._create(payload)
            else:
                r.raise_for_status()
        except requests.ConnectionError:
            raise CustomerApiError("Connection to discounts server failed")
        except requests.Timeout:
            raise CustomerApiError("Connection to discounts server timed out")
        except requests.TooManyRedirects:
            raise CustomerApiError("Too many redirects to discounts server")
        except requests.HTTPError as e:
            raise CustomerApiError(e)

    def _create(self, payload):
        """Create the customer represented by the payload token."""
        logger.info("Create new customer record")

        url = "/".join((self.provider.api_base_url, self.agency.merchant_id, self.provider.customers_endpoint))
        payload.update({"customer_ref": uuid.uuid4(), "is_registered": True})

        r = self._post(url, payload)
        r.raise_for_status()

        return CustomerResponse(r)

    def _update(self, customer_id, customer_ref):
        """Update a customer using their unique info."""
        logger.info("Update existing customer record")

        if customer_id is None:
            raise ValueError("customer_id")
        if customer_ref is None:
            raise ValueError("customer_ref")

        url = "/".join((self.provider.api_base_url, self.agency.merchant_id, self.provider.customer_endpoint, customer_id))
        payload = {"customer_ref": customer_ref, "is_registered": True}

        r = self._patch(url, payload)
        r.raise_for_status()

        return CustomerResponse(r)


class GroupApiError(Exception):
    """Error calling Group API."""

    pass


class GroupResponse:
    """Discount Provider Customer Group API response."""

    def __init__(self, response, payload=None):
        if payload is None:
            logger.info("Read group details from response")
            try:
                payload = response.json()
            except ValueError:
                raise GroupApiError("Invalid response format")
        else:
            logger.info("Read group details from argument")

        self.customer_ids = payload.get("customer_ids", [])
        self.updated_count = len(self.customer_ids)
        self.updated_customer_id = self.customer_ids[0] if self.updated_count == 1 else None


class GroupClient(Client):
    """Discounts Provider Customer Group API client."""

    def enroll_customer(self, customer_id, group_id):
        """Enroll the customer in the group."""
        logger.info("Enroll customer in product group")

        if customer_id is None:
            raise ValueError("customer_id")
        if group_id is None:
            raise ValueError("group_id")

        url = "/".join((self.provider.api_base_url, self.agency.merchant_id, self.provider.group_endpoint, group_id))
        payload = {"customer_ids": [customer_id]}

        try:
            r = self._patch(url, payload)

            if r.status_code in (200, 201):
                return GroupResponse(r)
            elif r.status_code == 500:
                # 500 indicates the customer already exists in the group
                return GroupResponse(r, payload=payload)
            else:
                r.raise_for_status()
        except requests.ConnectionError:
            raise GroupApiError("Connection to discounts server failed")
        except requests.Timeout:
            raise GroupApiError("Connection to discounts server timed out")
        except requests.TooManyRedirects:
            raise GroupApiError("Too many redirects to discounts server")
        except requests.HTTPError as e:
            raise GroupApiError(e)
