"""
The core application: analytics implementation.
"""
import logging
import time
import uuid

import requests

from benefits.settings import ANALYTICS_KEY
from . import session


logger = logging.getLogger(__name__)


class ApiError(Exception):
    """Error calling the Analytics API."""

    pass


class Event:
    """Represents a single analytics event."""

    def __init__(self, request, event_type):
        self.event_type = event_type
        self.insert_id = str(uuid.uuid4())
        self.session_id = session.start(request)
        self.time = int(time.time() * 1000)
        self.user_id = session.uid(request)


class Client:
    """Analytics API client"""

    def __init__(self):
        logger.debug("Initialize Analytics API Client")
        self.headers = {"Accept": "*/*", "Content-type": "application/json"}
        self.url = "https://api2.amplitude.com/2/httpapi"

    def _payload(self, events):
        return {"api_key": ANALYTICS_KEY, "events": events}

    def send(self, event):
        """Send a single event."""
        logger.debug("Sending a single event.")
        self.batch([event])

    def batch(self, events):
        """Send a batch of events."""
        logger.debug(f"Sending a batch of {len(events)} events.")
        r = requests.post(self.url, headers=self.headers, data=self._payload(events))

        if r.status_code == 200:
            logger.debug("Batch sent successfully")
        elif r.status_code == 400:
            logger.error("Batch request was invalid", exc_info=r.json())
        elif r.status_code == 413:
            logger.error("Batch payload was too large", exc_info=r.json())
        elif r.status_code == 429:
            logger.error("Batch contained too many requests for some users", exc_info=r.json())
        else:
            logger.error("Batch failed to send", exc_info=r.json())
