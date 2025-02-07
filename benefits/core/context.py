from dataclasses import dataclass, asdict

from django.utils.translation import gettext_lazy as _


@dataclass
class AgencyIndex:
    headline: str

    def dict(self):
        return asdict(self)


index_context = {
    "cst": AgencyIndex(headline=_("Get a reduced fare on CST public transportation when you tap to ride")),
    "mst": AgencyIndex(headline=_("Get a reduced fare on MST public transportation when you tap to ride")),
    "nevco": AgencyIndex(
        headline=_("Get a reduced fare on Nevada County Connects public transportation when you tap to ride")
    ),
    "sacrt": AgencyIndex(headline=_("Get a reduced fare on SacRT buses when you tap to ride")),
    "sbmtd": AgencyIndex(headline=_("Get a reduced fare on Santa Barbara MTD buses when you tap to ride")),
}
