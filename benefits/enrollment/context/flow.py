from dataclasses import dataclass, asdict
from typing import Optional

from benefits.core.context import AgencySlug, SystemName, formatted_gettext_lazy as _


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


@dataclass
class EnrollmentSuccess:
    success_message: str
    thank_you_message: str

    def dict(self):
        return asdict(self)


class DefaultEnrollmentSuccess(EnrollmentSuccess):
    def __init__(self, transportation_type):
        super().__init__(
            success_message=_(
                "You were not charged anything today. When boarding {transportation_type}, tap your contactless card and you "
                "will be charged a reduced fare. You will need to re-enroll if you choose to change the card you use to "
                "pay for transit service.",
                transportation_type=transportation_type,
            ),
            thank_you_message=_("Thank you for using Cal-ITP Benefits!"),
        )


class AgencyCardEnrollmentSuccess(EnrollmentSuccess):
    def __init__(self, transit_benefit, transportation_type):
        super().__init__(
            success_message=_(
                "Your contactless card is now enrolled in {transit_benefit}. When boarding {transportation_type}, tap this "
                "card and you will be charged a reduced fare. You will need to re-enroll if you choose to change the card you "
                "use to pay for transit service.",
                transit_benefit=transit_benefit,
                transportation_type=transportation_type,
            ),
            thank_you_message=_("You were not charged anything today. Thank you for using Cal-ITP Benefits!"),
        )


enrollment_success = {
    AgencySlug.CST.value: DefaultEnrollmentSuccess(
        transportation_type=_("a CST bus"),
    ),
    SystemName.AGENCY_CARD.value: AgencyCardEnrollmentSuccess(
        transit_benefit=_("a CST Agency Card transit benefit"), transportation_type=_("a CST bus")
    ),
    AgencySlug.MST.value: DefaultEnrollmentSuccess(transportation_type=_("an MST bus")),
    SystemName.COURTESY_CARD.value: AgencyCardEnrollmentSuccess(
        transit_benefit=_("an MST Courtesy Card transit benefit"), transportation_type="an MST bus"
    ),
    AgencySlug.NEVCO.value: DefaultEnrollmentSuccess(transportation_type=_("a Nevada County Connects bus")),
    AgencySlug.SACRT.value: DefaultEnrollmentSuccess(transportation_type=_("a SacRT bus")),
    AgencySlug.SBMTD.value: DefaultEnrollmentSuccess(transportation_type=_("an SBMTD bus")),
    SystemName.REDUCED_FARE_MOBILITY_ID.value: AgencyCardEnrollmentSuccess(
        transit_benefit=_("an SBMTD Reduced Fare Mobility ID transit benefit"), transportation_type=_("an SBMTD bus")
    ),
    AgencySlug.VCTC.value: DefaultEnrollmentSuccess(transportation_type=_("a Ventura County Transportation Commission bus")),
}
