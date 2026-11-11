import logging

from django.shortcuts import redirect

from benefits.metro_mobility_wallet.session import Session

logger = logging.getLogger(__name__)


class TermsAcceptanceRequiredMixin:
    """Mixin intended for use with a class-based view as the first in the MRO.

    If the user has not accepted the Mobility Wallet Program Terms, redirect them to the Terms page
    """

    def dispatch(self, request, *args, **kwargs):
        session = Session(self.request)
        if session.accepted_terms:
            return super().dispatch(request, *args, **kwargs)
        else:
            logger.warning("User has not accepted Mobility Wallet Program Terms")
            return redirect("metro_mobility_wallet:terms")
