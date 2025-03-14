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
}
