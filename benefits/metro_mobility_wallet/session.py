import logging

from django.http import HttpRequest

logger = logging.getLogger(__name__)


class Session:
    def __init__(self, request: HttpRequest):
        """Initialize a new Metro Mobility Wallet session wrapper for this request"""

        self.request = request
        self.session = request.session
