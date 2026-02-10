from dataclasses import asdict, dataclass

from benefits.core.context import SystemName, formatted_gettext_lazy as _


@dataclass
class EligibilityUnverified:
    headline_text: str
    body_text: str
    button_text: str

    def dict(self):
        return asdict(self)


class AgencyCardEligibilityUnverified(EligibilityUnverified):
    def __init__(self, agency_card):
        super().__init__(
            headline_text=_("Your card information may not have been entered correctly."),
            body_text=_(
                "The number and last name must be entered exactly as they appear on your {agency_card}. "
                "Please check your card and try again, or contact your transit agency for help.",
                agency_card=agency_card,
            ),
            button_text=_("Try again"),
        )


eligibility_unverified = {
    SystemName.AGENCY_CARD.value: AgencyCardEligibilityUnverified(agency_card=_("CST Agency Card")),
    SystemName.COURTESY_CARD.value: AgencyCardEligibilityUnverified(agency_card=_("MST Courtesy Card")),
    SystemName.REDUCED_FARE_MOBILITY_ID.value: AgencyCardEligibilityUnverified(
        agency_card=_("SBMTD Reduced Fare Mobility ID card")
    ),
}
