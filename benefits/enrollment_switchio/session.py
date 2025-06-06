import logging

from django.http import HttpRequest

logger = logging.getLogger(__name__)


class Session:

    _keys_registration_id = "enrollment_switchio_registration_id"
    _keys_gateway_url = "enrollment_switchio_gateway_url"

    def __init__(self, request: HttpRequest, reset: bool = False, registration_id: str = None, gateway_url: str = None):
        """Initialize a new Switchio session wrapper for this request."""

        self.request = request
        self.session = request.session

        if reset:
            self.registration_id = None
            self.gateway_url = None
        if registration_id:
            self.registration_id = registration_id
        if gateway_url:
            self.gateway_url = gateway_url

    @property
    def registration_id(self) -> str:
        """Get the registration ID from the request's session, or None."""
        return self.session.get(self._keys_registration_id)

    @registration_id.setter
    def registration_id(self, value: str) -> None:
        self.session[self._keys_registration_id] = value

    @property
    def gateway_url(self) -> str:
        """Get the gateway URL from the request's session, or None."""
        return self.session.get(self._keys_gateway_url)

    @gateway_url.setter
    def gateway_url(self, value: str) -> None:
        self.session[self._keys_gateway_url] = value
