"""
The core application: context processors for enriching request context data.
"""
from eligibility_verification.settings import DEBUG

from . import session


def debug(request):
    """Context processor adds debug information to request context."""

    context = dict(debug=DEBUG)

    if DEBUG:
        agency = session.agency(request) or None
        context.update(dict(agency=agency.slug if agency else "None"))

    return context
