import logging

from django.http import HttpRequest

logger = logging.getLogger(__name__)


class Session:

    _keys_registration_id = "enrollment_switchio_registration_id"

    def __init__(self, request: HttpRequest, reset: bool = False, registration_id: str = None):
        """Initialize a new Switchio session wrapper for this request."""

        self.request = request
        self.session = request.session

        if reset:
            self.registration_id = None
        if registration_id:
            self.registration_id = registration_id

    @property
    def registration_id(self) -> str:
        """Get the registration ID from the request's session, or None."""
        return self.session.get(self._keys_registration_id)

    @registration_id.setter
    def registration_id(self, value: str) -> None:
        self.session[self._keys_registration_id] = value
