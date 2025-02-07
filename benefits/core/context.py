from dataclasses import dataclass, asdict

from django.db import models
from django.utils.translation import gettext_lazy as _


@dataclass
class AgencyIndex:
    headline: str

    def dict(self):
        return asdict(self)


class Agency(models.TextChoices):
    CST = "cst"
    MST = "mst"
    NEVCO = "nevco"
    SACRT = "sacrt"
    SBMTD = "sbmtd"


index_context = {
    Agency.CST: AgencyIndex(headline=_("Get a reduced fare on CST public transportation when you tap to ride")),
    Agency.MST: AgencyIndex(headline=_("Get a reduced fare on MST public transportation when you tap to ride")),
    Agency.NEVCO: AgencyIndex(
        headline=_("Get a reduced fare on Nevada County Connects public transportation when you tap to ride")
    ),
    Agency.SACRT: AgencyIndex(headline=_("Get a reduced fare on SacRT buses when you tap to ride")),
    Agency.SBMTD: AgencyIndex(headline=_("Get a reduced fare on Santa Barbara MTD buses when you tap to ride")),
}
