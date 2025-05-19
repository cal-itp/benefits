import logging
import time

from django.http import HttpRequest

logger = logging.getLogger(__name__)


class Session:

    _keys_access_token = "enrollment_littlepay_access_token"
    _keys_access_token_expiry = "enrollment_littlepay_access_token_expiry"

    def __init__(self, request: HttpRequest, reset: bool = False, access_token: str = None, access_token_expiry: str = None):
        """Initialize a new Littlepay session wrapper for this request."""

        self.request = request
        self.session = request.session

        if reset:
            self.access_token = None
            self.access_token_expiry = None
        if access_token:
            self.access_token = access_token
        if access_token_expiry:
            self.access_token_expiry = access_token_expiry

    @property
    def access_token(self) -> str:
        """Get the card tokenization access token from the request's session, or None."""
        return self.session.get(self._keys_access_token)

    @access_token.setter
    def access_token(self, value: str) -> None:
        self.session[self._keys_access_token] = value

    @property
    def access_token_expiry(self) -> int:
        """Get the card tokenization access token's expiry time from the request's session, or None."""
        return self.session.get(self._keys_access_token_expiry)

    @access_token_expiry.setter
    def access_token_expiry(self, value: int) -> None:
        self.session[self._keys_access_token_expiry] = value

    def access_token_valid(self):
        """True if the request's session is configured with a valid card tokenization access token. False otherwise."""
        if bool(self.access_token):
            exp = self.access_token_expiry
            # ensure token does not expire in the next 5 seconds
            valid = exp is None or exp > (time.time() + 5)
            return valid
        else:
            return False
