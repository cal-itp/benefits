"""
The core application: context processors for enriching request context data.
"""
from eligibility_verification.settings import DEBUG

from . import session


def debug(request):
    """Context processor adds debug information to request context."""
    context = {}

    if DEBUG:
        context.update(dict(debug=session.context_dict(request)))

    return context
