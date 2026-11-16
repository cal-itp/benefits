import logging

from cdt_identity.session import Session as OAuthSession
from django.http import HttpRequest

from benefits.core import session
from benefits.core.models.enrollment import EnrollmentFlow, SystemName

logger = logging.getLogger(__name__)


class Session(OAuthSession):

    _keys_accepted_terms = "mmw_accepted_terms"

    def __init__(self, request: HttpRequest):
        """Initialize a new Metro Mobility Wallet session wrapper for this request"""

        session.update(request, flow=self.flow)
        super().__init__(
            request=request,
            client_config=self.flow.oauth_config,
            claims_request=self.flow.claims_request,
        )

    @property
    def flow(self) -> EnrollmentFlow:
        return EnrollmentFlow.objects.filter(system_name=SystemName.METRO_MOBILITY_WALLET).first()

    @property
    def accepted_terms(self) -> bool:
        return self.session.get(self._keys_accepted_terms, False)

    @accepted_terms.setter
    def accepted_terms(self, value: bool) -> None:
        self.session[self._keys_accepted_terms] = value
