import logging

from . import session
from .middleware import user_error

logger = logging.getLogger(__name__)


class AgencySessionRequiredMixin:
    """Mixin intended for use with a class-based view as the first in the MRO.

    Gets the active `TransitAgency` out of session and sets an attribute on `self`.

    If the session is not configured with an agency, return a user error.
    """

    def dispatch(self, request, *args, **kwargs):
        if session.active_agency(request):
            self.agency = session.agency(request)
            return super().dispatch(request, *args, **kwargs)
        else:
            logger.warning("Session not configured with an active agency")
            return user_error(request)
