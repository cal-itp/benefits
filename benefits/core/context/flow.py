from dataclasses import asdict, dataclass

from django.db import models
from django.utils.translation import gettext_lazy as _


class SystemName(models.TextChoices):
    AGENCY_CARD = "agency_card"
    CALFRESH = "calfresh"
    COURTESY_CARD = "courtesy_card"
    MEDICARE = "medicare"
    OLDER_ADULT = "senior"
    REDUCED_FARE_MOBILITY_ID = "mobility_pass"
    VETERAN = "veteran"


@dataclass
class FlowHelp:

    id: str
    headline: str
    text: str

    def dict(self):
        return asdict(self)


flows_help = {
    SystemName.AGENCY_CARD.value: [
        FlowHelp(
            id="cst-agency-card",
            headline=_("What is an Agency Card?"),
            text=_(
                "California State Transit issues Agency Cards to riders who qualify for a number of reduced fare "
                "programs. This transit benefit may need to be renewed in the future based on the expiration date of the "
                'Agency Card. Learn more at the <a href="https://www.agency-website.com" target="_blank" rel="noopener noreferrer">www.agency-website.com</a>.'  # noqa: E501
            ),
        )
    ],
    SystemName.CALFRESH.value: [
        FlowHelp(
            id="calfresh-transit-benefit",
            headline=_("How do I know if I’m eligible for the transit benefit for CalFresh Cardholders?"),
            text=_(
                "We verify your eligibility as a CalFresh Cardholder by confirming you have received funds in your "
                "CalFresh account at any point in the last three months. This means you are eligible for a transit "
                "benefit even if you did not receive funds in your CalFresh account this month or last month."
            ),
        ),
        FlowHelp(
            id="calfresh-transit-benefit-no-account-changes",
            headline=_("Will this transit benefit change my CalFresh account?"),
            text=_("No. Your monthly CalFresh allotment will not change."),
        ),
        FlowHelp(
            id="calfresh-transit-benefit-enrollment",
            headline=_("Do I need my Golden State Advantage card to enroll?"),
            text=_(
                "No, you do not need your physical EBT card to enroll. We use information from Login.gov and the "
                "California Department of Social Services to enroll you in the benefit."
            ),
        ),
        FlowHelp(
            id="calfresh-transit-benefit-payment",
            headline=_("Can I use my Golden State Advantage card to pay for transit rides?"),
            text=_(
                "No. You can not use your EBT or P-EBT card to pay for public transportation. "
                "When you tap to ride, use your personal contactless debit or credit card to pay for public transportation."  # noqa: E501
            ),
        ),
    ],
}
