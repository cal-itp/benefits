from dataclasses import dataclass, asdict
from typing import Optional

from benefits.core.context import SystemName, formatted_gettext_lazy as _


@dataclass
class EnrollmentIndex:
    headline: str
    next_step: str
    partner_post_link: str
    alert_include: Optional[str] = ""

    def dict(self):
        return asdict(self)


class DefaultEnrollmentIndex(EnrollmentIndex):
    def __init__(
        self,
        headline=_("Your eligibility is confirmed! You’re almost there."),
        next_step=_("The next step is to enroll the contactless card you will use to tap to ride for a reduced fare."),
        partner_post_link=_(", to enter your contactless card details."),
        alert_include="",
    ):
        super().__init__(
            headline=headline, next_step=next_step, partner_post_link=partner_post_link, alert_include=alert_include
        )


class AgencyCardEnrollmentIndex(DefaultEnrollmentIndex):
    def __init__(self):
        super().__init__(headline=_("We found your record! Now let’s enroll your contactless card."))


class CalFreshEnrollmentIndex(DefaultEnrollmentIndex):
    def __init__(self):
        super().__init__(
            next_step=_("The next step is to connect your contactless card to your transit benefit"),
            partner_post_link=".",
            alert_include="enrollment/includes/alert-box--warning--calfresh.html",
        )


enrollment_index = {
    SystemName.AGENCY_CARD: AgencyCardEnrollmentIndex(),
    SystemName.COURTESY_CARD: AgencyCardEnrollmentIndex(),
    SystemName.REDUCED_FARE_MOBILITY_ID: AgencyCardEnrollmentIndex(),
    SystemName.CALFRESH: CalFreshEnrollmentIndex(),
}
