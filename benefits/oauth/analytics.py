"""
The oauth application: analytics implementation.
"""
from benefits.core import analytics as core
from benefits.settings import OAUTH_CLIENT_NAME


class OAuthEvent(core.Event):
    """Base OAuth analytics event."""

    def __init__(self, request, event_type):
        super().__init__(request, event_type)
        self.update_event_properties(auth_provider=OAUTH_CLIENT_NAME)


class StartedSignInEvent(OAuthEvent):
    """Analytics event representing the beginning of the OAuth sign in flow."""

    def __init__(self, request):
        super().__init__(request, "started sign in")


class FinishedSignInEvent(OAuthEvent):
    """Analytics event representing the end of the OAuth sign in flow."""

    def __init__(self, request):
        super().__init__(request, "finished sign in")


class SignedOutEvent(OAuthEvent):
    """Analytics event representing application sign out."""

    def __init__(self, request):
        super().__init__(request, "signed out")


def started_sign_in(request):
    """Send the "started sign in" analytics event."""
    core.send_event(StartedSignInEvent(request))


def finished_sign_in(request):
    """Send the "finished sign in" analytics event."""
    core.send_event(FinishedSignInEvent(request))


def signed_out(request):
    """Send the "signed out" analytics event."""
    core.send_event(SignedOutEvent(request))
