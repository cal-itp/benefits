import logging

from django.http import HttpRequest

from benefits.core.models.enrollment import EnrollmentFlow, SystemName

logger = logging.getLogger(__name__)


class Session:

    _keys_agreed_to_terms = "mmw_agreed_to_terms"

    def __init__(self, request: HttpRequest):
        """Initialize a new Metro Mobility Wallet session wrapper for this request"""

        self.request = request
        self.session = request.session

    @property
    def flow(self) -> EnrollmentFlow:
        return EnrollmentFlow.objects.filter(system_name=SystemName.METRO_MOBILITY_WALLET).first()

    @property
    def agreed_to_terms(self) -> bool:
        return self.session.get(self._keys_agreed_to_terms, False)

    @agreed_to_terms.setter
    def agreed_to_terms(self, value: bool) -> None:
        self.session[self._keys_agreed_to_terms] = value
