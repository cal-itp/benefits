"""
The core application: analytics implementation.
"""
import itertools
import json
import logging
import time
import uuid

import requests

from benefits import VERSION
from benefits.settings import ANALYTICS_KEY
from . import session


logger = logging.getLogger(__name__)


class ApiError(Exception):
    """Error calling the Analytics API."""

    pass


class Event:
    """Represents a single analytics event."""

    _counter = itertools.count()

    def __init__(self, request, event_type, **kwargs):
        self.app_version = VERSION
        self.event_type = event_type
        self.insert_id = str(uuid.uuid4())
        self.language = session.language(request)
        self.session_id = session.start(request)
        self.time = int(time.time() * 1000)
        self.user_id = session.uid(request)
        self.event_properties = kwargs
        # event is initialized, consume next counter
        self.event_id = next(Event._counter)

    def __str__(self):
        return json.dumps(self.__dict__)


class Client:
    """Analytics API client"""

    def __init__(self):
        logger.debug("Initialize Analytics API Client")
        self.headers = {"Accept": "*/*", "Content-type": "application/json"}
        self.url = "https://api2.amplitude.com/2/httpapi"

    def _payload(self, events):
        if not isinstance(events, list):
            events = [events]
        return {"api_key": ANALYTICS_KEY, "events": [e.__dict__ for e in events]}

    def send(self, event):
        """Send an analytics event."""
        if not ANALYTICS_KEY:
            logger.warning(f"ANALYTICS_KEY is not configured, cannot send: {event}")
            return

        payload = self._payload(event)
        logger.debug(f"Sending event payload: {payload}")
        r = requests.post(self.url, headers=self.headers, json=payload)

        if r.status_code == 200:
            logger.debug(f"Event sent successfully: {r.json()}")
        elif r.status_code == 400:
            logger.error(f"Event request was invalid: {r.json()}")
        elif r.status_code == 413:
            logger.error(f"Event payload was too large: {r.json()}")
        elif r.status_code == 429:
            logger.error(f"Event contained too many requests for some users: {r.json()}")
        else:
            logger.error(f"Event failed to send: {r.json()}")


def send_event(event=None, request=None, event_type=None, **kwargs):
    """
    Send an analytics event. If :event: is an Event instance, send that.
    Otherwise :request: and :event_type: are required to construct a new Event instance.
    Extra kwargs are added as event_properties (must be JSON-serializable).
    """
    if isinstance(event, Event):
        event.event_properties.update(kwargs)
        Client().send(event)
    elif all((request, event_type)):
        event = Event(request, event_type, **kwargs)
        Client().send(event)
    else:
        raise ValueError("Either pass an Event instance, or Django request object and event type string")
