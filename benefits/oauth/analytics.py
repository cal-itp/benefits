"""
The oauth application: analytics implementation.
"""

from benefits.core import analytics as core, session


class OAuthEvent(core.Event):
    """Base OAuth analytics event."""

    def __init__(self, request, event_type):
        super().__init__(request, event_type)
        verifier = session.verifier(request)
        if verifier and verifier.uses_claims_verification:
            self.update_event_properties(auth_provider=verifier.claims_provider.client_name)


class OAuthErrorEvent(OAuthEvent):
    """Analytics event representing an error using an OAuth client."""

    def __init__(self, request, message, operation):
        super().__init__(request, "oauth error")
        self.update_event_properties(message=message, operation=operation)


class StartedSignInEvent(OAuthEvent):
    """Analytics event representing the beginning of the OAuth sign in flow."""

    def __init__(self, request):
        super().__init__(request, "started sign in")


class CanceledSignInEvent(OAuthEvent):
    """Analytics event representing the canceling of application sign in."""

    def __init__(self, request):
        super().__init__(request, "canceled sign in")


class FinishedSignInEvent(OAuthEvent):
    """Analytics event representing the end of the OAuth sign in flow."""

    def __init__(self, request, error=None):
        super().__init__(request, "finished sign in")
        if error is not None:
            self.update_event_properties(error_code=error)


class StartedSignOutEvent(OAuthEvent):
    """Analytics event representing the beginning of application sign out."""

    def __init__(self, request):
        super().__init__(request, "started sign out")


class FinishedSignOutEvent(OAuthEvent):
    """Analytics event representing the end of application sign out."""

    def __init__(self, request):
        super().__init__(request, "finished sign out")
        self.update_event_properties(origin=session.origin(request))


def error(request, message, operation):
    """Send the "oauth error" analytics event, specifying the message and operation"""
    core.send_event(OAuthErrorEvent(request, message, operation))


def started_sign_in(request):
    """Send the "started sign in" analytics event."""
    core.send_event(StartedSignInEvent(request))


def canceled_sign_in(request):
    """Send the "canceled sign in" analytics event."""
    core.send_event(CanceledSignInEvent(request))


def finished_sign_in(request, error=None):
    """Send the "finished sign in" analytics event."""
    core.send_event(FinishedSignInEvent(request, error))


def started_sign_out(request):
    """Send the "started signed out" analytics event."""
    core.send_event(StartedSignOutEvent(request))


def finished_sign_out(request):
    """Send the "finished sign out" analytics event."""
    core.send_event(FinishedSignOutEvent(request))
