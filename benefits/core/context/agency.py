from dataclasses import dataclass, asdict

from django.db import models
from django.utils.translation import gettext_lazy as _


class AgencySlug(models.TextChoices):
    # raw value, display value
    CST = "cst", "cst"
    MST = "mst", "mst"
    NEVCO = "nevco", "nevco"
    SACRT = "sacrt", "sacrt"
    SBMTD = "sbmtd", "sbmtd"


@dataclass
class AgencyIndex:
    headline: str

    def dict(self):
        return asdict(self)


agency_index = {
    AgencySlug.CST.value: AgencyIndex(headline=_("Get a reduced fare on CST public transportation when you tap to ride")),
    AgencySlug.MST.value: AgencyIndex(headline=_("Get a reduced fare on MST public transportation when you tap to ride")),
    AgencySlug.NEVCO.value: AgencyIndex(
        headline=_("Get a reduced fare on Nevada County Connects public transportation when you tap to ride")
    ),
    AgencySlug.SACRT.value: AgencyIndex(headline=_("Get a reduced fare on SacRT buses when you tap to ride")),
    AgencySlug.SBMTD.value: AgencyIndex(headline=_("Get a reduced fare on Santa Barbara MTD buses when you tap to ride")),
}
