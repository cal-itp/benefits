"""
The oauth application: analytics implementation.
"""
from benefits.core import analytics as core
from benefits.settings import OAUTH_CLIENT_NAME


class OAuthEvent(core.Event):
    def __init__(self, request, event_type):
        """Base OAuth analytics event."""
        super().__init__(request, event_type)
        self.update_event_properties(auth_provider=OAUTH_CLIENT_NAME)
