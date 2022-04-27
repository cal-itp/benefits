"""
The core application: analytics implementation.
"""
import itertools
import json
import logging
import re
import time
import uuid

from django.conf import settings
import requests

from benefits import VERSION
from . import session


logger = logging.getLogger(__name__)


class Event:
    """Base analytics event of a given type, including attributes from request's session."""

    _counter = itertools.count()
    _domain_re = re.compile(r"^(?:https?:\/\/)?(?:[^@\n]+@)?(?:www\.)?([^:\/\n?]+)", re.IGNORECASE)

    def __init__(self, request, event_type, **kwargs):
        self.app_version = VERSION
        self.device_id = session.did(request)
        self.event_properties = {}
        self.event_type = str(event_type).lower()
        self.insert_id = str(uuid.uuid4())
        self.language = session.language(request)
        self.session_id = session.start(request)
        self.time = int(time.time() * 1000)
        self.user_id = session.uid(request)
        self.user_properties = {}
        self.__dict__.update(kwargs)

        agency = session.agency(request)
        name = agency.long_name if agency else None

        self.update_event_properties(path=request.path, provider_name=name)

        uagent = request.headers.get("user-agent")

        ref = request.headers.get("referer")
        match = Event._domain_re.match(ref) if ref else None
        refdom = match.group(1) if match else None

        self.update_user_properties(referrer=ref, referring_domain=refdom, user_agent=uagent, provider_name=name)

        # event is initialized, consume next counter
        self.event_id = next(Event._counter)

    def __str__(self):
        return json.dumps(self.__dict__)

    def update_event_properties(self, **kwargs):
        """Merge kwargs into the self.event_properties dict."""
        self.event_properties.update(kwargs)

    def update_user_properties(self, **kwargs):
        """Merge kwargs into the self.user_properties dict."""
        self.user_properties.update(kwargs)


class ViewedPageEvent(Event):
    """Analytics event representing a single page view."""

    def __init__(self, request):
        super().__init__(request, "viewed page")


class ChangedLanguageEvent(Event):
    """Analytics event representing a change in the app's language."""

    def __init__(self, request, new_lang):
        super().__init__(request, "changed language")
        self.update_event_properties(language=new_lang)


class Client:
    """Analytics API client"""

    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {"Accept": "*/*", "Content-type": "application/json"}
        self.url = "https://api2.amplitude.com/2/httpapi"
        logger.debug(f"Initialize Client for {self.url}")

    def _payload(self, events):
        if not isinstance(events, list):
            events = [events]
        return {"api_key": self.api_key, "events": [e.__dict__ for e in events]}

    def send(self, event):
        """Send an analytics event."""
        if not isinstance(event, Event):
            raise ValueError("event must be an Event instance")

        if not self.api_key:
            logger.warning(f"api_key is not configured, cannot send event: {event}")
            return

        try:
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
                logger.error(f"Failed to send event: {r.json()}")

        except Exception:
            logger.error(f"Failed to send event: {event}")


client = Client(settings.ANALYTICS_KEY)


def send_event(event):
    """Send an analytics event."""
    if isinstance(event, Event):
        client.send(event)
    else:
        raise ValueError("event must be an Event instance")
