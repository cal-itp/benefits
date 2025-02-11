from dataclasses import dataclass, asdict

from django.db import models
from django.utils.translation import gettext_lazy as _


@dataclass
class AgencyIndex:
    headline: str

    def dict(self):
        return asdict(self)


class AgencySlug(models.TextChoices):
    # raw value, display value
    CST = "cst", "cst"
    MST = "mst", "mst"
    NEVCO = "nevco", "nevco"
    SACRT = "sacrt", "sacrt"
    SBMTD = "sbmtd", "sbmtd"


index_context = {
    AgencySlug.CST: AgencyIndex(headline=_("Get a reduced fare on CST public transportation when you tap to ride")),
    AgencySlug.MST: AgencyIndex(headline=_("Get a reduced fare on MST public transportation when you tap to ride")),
    AgencySlug.NEVCO: AgencyIndex(
        headline=_("Get a reduced fare on Nevada County Connects public transportation when you tap to ride")
    ),
    AgencySlug.SACRT: AgencyIndex(headline=_("Get a reduced fare on SacRT buses when you tap to ride")),
    AgencySlug.SBMTD: AgencyIndex(headline=_("Get a reduced fare on Santa Barbara MTD buses when you tap to ride")),
}
