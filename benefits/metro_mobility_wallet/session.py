import logging

from django.http import HttpRequest

from benefits.core.models.enrollment import EnrollmentFlow, SystemName

logger = logging.getLogger(__name__)


class Session:
    def __init__(self, request: HttpRequest):
        """Initialize a new Metro Mobility Wallet session wrapper for this request"""

        self.request = request
        self.session = request.session

    @property
    def flow(self) -> EnrollmentFlow:
        return EnrollmentFlow.objects.filter(system_name=SystemName.METRO_MOBILITY_WALLET).first()
