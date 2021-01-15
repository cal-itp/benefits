"""
The discounts application: Discounts API implementation.
"""
import time

import requests

from benefits.core.api import Response


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


class Client():
    """Discounts Provider API HTTP client."""

    def __init__(self, agency):
        self.agency = agency
        self.provider = agency.discount_provider

    def access_token(self):
        """Obtain an access token to use for integrating with other APIs."""

        url = "/".join((
            self.provider.api_base_url,
            self.agency.merchant_id,
            self.provider.api_access_token_endpoint
        ))

        payload = {
            self.provider.api_access_token_request_key:
            self.provider.api_access_token_request_val
        }

        headers = {"Accept": "application/json", "Content-type": "application/json"}

        try:
            r = requests.post(url, json=payload, headers=headers)
        except requests.ConnectionError as ex:
            return Response(500, error=ex, message="Access token: Connection to discounts server failed")
        except requests.Timeout as ex:
            return Response(500, error=ex, message="Access token: Connection to discounts server timed out")
        except requests.TooManyRedirects as ex:
            return Response(500, error=ex, message="Access token: Too many redirects to discounts server")

        if r.status_code == 200:
            return AccessTokenResponse(r, self.agency, self.provider)
        elif r.status_code == 400:
            return Response(r.status_code, message="Access token: Bad request")
        elif r.status_code == 404:
            return Response(r.status_code, message="Access token: Not found")
        else:
            return Response(r.status_code, message="Access token: Error")
