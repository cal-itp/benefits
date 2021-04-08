"""
The core application: analytics implementation.
"""
import itertools
import json
import logging
import re
import time
import uuid

import requests

from benefits import VERSION
from benefits.settings import ANALYTICS_KEY
from . import session


logger = logging.getLogger(__name__)


class Event:
    _counter = itertools.count()

    def __init__(self, request, event_type, **kwargs):
        """A single analytics event of the given type, including attributes from request's session."""
        self.app_version = VERSION
        self.event_properties = {}
        self.event_type = str(event_type).lower()
        self.insert_id = str(uuid.uuid4())
        self.language = session.language(request)
        self.session_id = session.start(request)
        self.time = int(time.time() * 1000)
        self.user_id = session.uid(request)
        self.user_properties = {}
        self.update(**kwargs)
        # event is initialized, consume next counter
        self.event_id = next(Event._counter)

    def __str__(self):
        return json.dumps(self.__dict__)

    def update(self, **kwargs):
        self.__dict__.update(kwargs)


class ViewPageEvent(Event):
    _domain_re = re.compile(r"^(?:https?:\/\/)?(?:[^@\n]+@)?(?:www\.)?([^:\/\n?]+)", re.IGNORECASE)

    def __init__(self, request, page_name, **kwargs):
        """Analytics event representing a single pageview, with common properties."""
        super().__init__(request, f"view page {page_name}", **kwargs)

        uagent = request.headers.get("user-agent")

        ref = request.headers.get("referer")
        match = ViewPageEvent._domain_re.match(ref) if ref else None
        refdom = match.group(1) if match else None

        agency = session.agency(request)

        self.update(
            event_properties=dict(path=request.path, provider_name=agency.long_name if agency else None),
            user_properties=dict(referrer=ref, referring_domain=refdom, user_agent=uagent),
        )


class ChangeLanguageEvent(Event):
    def __init__(self, request, new_lang, **kwargs):
        """Analytics event representing a change in the app's language."""
        super().__init__(request, "change language", **kwargs)
        self.update(event_properties=dict(language=new_lang))


class Client:
    def __init__(self, api_key):
        """Analytics API client"""
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
                logger.info(f"Event sent successfully: {r.json()}")
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


def send_event(event=None, request=None, event_type=None, **kwargs):
    """
    Send an analytics event. If :event: is an Event instance, use that.
    Otherwise :request: and :event_type: are required to construct a new Event instance.
    Extra kwargs are merged as event attributes (must be JSON-serializable).
    """
    if isinstance(event, Event):
        event.update(**kwargs)
        Client(ANALYTICS_KEY).send(event)
    elif all((request, event_type)):
        event = Event(request, event_type, **kwargs)
        Client(ANALYTICS_KEY).send(event)
    else:
        raise ValueError("Either pass an Event instance, or Django request object and event type string")
