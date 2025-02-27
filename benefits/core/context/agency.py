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


class EligibilityIndex:
    def __init__(self, form_text):
        if not isinstance(form_text, list):
            form_text = [form_text]

        self.form_text = form_text

    def dict(self):
        return dict(form_text=self.form_text)


eligibility_index = {
    AgencySlug.CST.value: EligibilityIndex(
        form_text=_(
            "Cal-ITP doesn’t save any of your information. All CST transit benefits reduce fares by 50% for bus service on fixed routes."  # noqa
        )
    ),
    AgencySlug.MST.value: EligibilityIndex(
        form_text=_(
            "Cal-ITP doesn’t save any of your information. All MST transit benefits reduce fares by 50% for bus service on fixed routes."  # noqa
        )
    ),
    AgencySlug.NEVCO.value: EligibilityIndex(
        form_text=_(
            "Cal-ITP doesn’t save any of your information. All Nevada County Connects transit benefits reduce fares by 50% for bus service on fixed routes."  # noqa
        )
    ),
    AgencySlug.SACRT.value: EligibilityIndex(
        form_text=[
            _(
                "Cal-ITP doesn’t save any of your information. All SacRT transit benefits reduce fares by 50% for bus service on fixed routes."  # noqa
            ),
            _(
                "With the new Tap2Ride fare system launching in 2025, SacRT riders that are eligible for discount fares can enroll below. The discount benefit will be available on all SacRT buses beginning in early 2025 and will include light rail tap devices later in the year."  # noqa
            ),
        ]
    ),
    AgencySlug.SBMTD.value: EligibilityIndex(
        form_text=_(
            "Cal-ITP doesn’t save any of your information. All SBMTD transit benefits reduce fares by 50% for bus service on fixed routes."  # noqa
        )
    ),
}
