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
    SystemName.COURTESY_CARD.value: [
        FlowHelp(
            id="mst-agency-card",
            headline=_("What is a Courtesy Card?"),
            text=_(
                "Monterey-Salinas Transit issues Courtesy Cards to riders who qualify for a number of reduced fare programs. "  # noqa: E501
                "This transit benefit may need to be renewed in the future based on the expiration date of the Courtesy Card. "  # noqa: E501
                'Learn more at the <a href="https://mst.org/riders-guide/how-to-ride/courtesy-card/" target="_blank" rel="noopener noreferrer">MST Riders Guide</a>.'  # noqa: E501
            ),
        )
    ],
    SystemName.MEDICARE.value: [
        FlowHelp(
            id="medicare-transit-benefit",
            headline=_("How do I know if I qualify for the Medicare Cardholder option?"),
            text=_(
                "You qualify for this option if you have a Medicare card. To enroll you will need an account with Medicare.gov. "  # noqa: E501
                "You will need to sign up for a Medicare.gov account if you do not currently have one. Deceased Medicare cardholders do not qualify."  # noqa: E501
            ),
        ),
        FlowHelp(
            id="medicare-transit-benefit-enrollment",
            headline=_("Do I need my Medicare card to enroll?"),
            text=_(
                "No, you do not need your physical Medicare card to enroll in a transit benefit. "
                "You will need the information on your card to create an account at Medicare.gov if you do not currently have an online account."  # noqa: E501
            ),
        ),
        FlowHelp(
            id="medicare-transit-benefit-payment",
            headline=_("Do I need to bring my Medicare card when I ride public transportation?"),
            text=_(
                "No, you do not need your physical Medicare card to use your transit benefit on public transportation. "
                "Once you have enrolled you can use your contactless debit or credit card to tap to ride with a reduced fare."  # noqa: E501
            ),
        ),
        FlowHelp(
            id="medicare-transit-benefit-recommended",
            headline=_("What if I qualify for more than one option?"),
            text=_(
                "You can enroll in any option you qualify for. We recommend enrolling in the Medicare Cardholder option if you qualify for it."  # noqa: 501
            ),
        ),
    ],
    SystemName.REDUCED_FARE_MOBILITY_ID.value: [
        FlowHelp(
            id="sbmtd-agency-card",
            headline=_("What is a Reduced Fare Mobility ID?"),
            text=_(
                "The Santa Barbara Metropolitan Transit District issues Reduced Fare Mobility ID cards to eligible riders. "  # noqa: E501
                "This transit benefit may need to be renewed in the future based on the expiration date of the Reduced Fare Mobility ID. "  # noqa: E501
                'Learn more at the <a href="https://sbmtd.gov/fares-passes/" target="_blank" rel="noopener noreferrer">SBMTD Fares & Passes</a>.'  # noqa: E501
            ),
        )
    ],
}
