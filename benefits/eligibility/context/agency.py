from django.utils.translation import gettext_lazy as _

from benefits.core.context import AgencySlug


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
            "Cal-ITP doesn’t save any of your information. "
            "All CST transit benefits reduce fares by 50%% for bus service on fixed routes.".replace("%%", "%")
        )
    ),
    AgencySlug.MST.value: EligibilityIndex(
        form_text=_(
            "Cal-ITP doesn’t save any of your information. "
            "All MST transit benefits reduce fares by 50%% for bus service on fixed routes.".replace("%%", "%")
        )
    ),
    AgencySlug.NEVCO.value: EligibilityIndex(
        form_text=_(
            "Cal-ITP doesn’t save any of your information. "
            "All Nevada County Connects transit benefits reduce fares by 50%% for bus service on fixed routes.".replace(
                "%%", "%"
            )
        )
    ),
    AgencySlug.SACRT.value: EligibilityIndex(
        form_text=[
            _(
                "Cal-ITP doesn’t save any of your information. "
                "All SacRT transit benefits reduce fares by 50%% for bus service on fixed routes.".replace("%%", "%")  # noqa
            ),
            _(
                "With the new Tap2Ride fare system launching in 2025, SacRT riders that are eligible for discount fares can "
                "enroll below. The discount benefit will be available on all SacRT buses beginning in early 2025 and will "
                "include light rail tap devices later in the year."  # noqa
            ),
        ]
    ),
    AgencySlug.SBMTD.value: EligibilityIndex(
        form_text=_(
            "Cal-ITP doesn’t save any of your information. "
            "All SBMTD transit benefits reduce fares by 50%% for bus service on fixed routes.".replace("%%", "%")
        )
    ),
}
