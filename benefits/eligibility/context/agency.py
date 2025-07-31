from benefits.core.context import AgencySlug, formatted_gettext_lazy as _


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
        form_text=_(
            "Cal-ITP doesn’t save any of your information. "
            "All SacRT transit benefits reduce fares by 50%% for bus service on fixed routes.".replace("%%", "%")
        )
    ),
    AgencySlug.SBMTD.value: EligibilityIndex(
        form_text=_(
            "Cal-ITP doesn’t save any of your information. "
            "All SBMTD transit benefits reduce fares by 50%% for bus service on fixed routes.".replace("%%", "%")
        )
    ),
    AgencySlug.VENTURA.value: EligibilityIndex(
        form_text=_(
            "Cal-ITP doesn’t save any of your information. "
            "All Ventura County Transportation Commission transit benefits "
            "reduce fares by 50%% for bus service on fixed routes.".replace("%%", "%")
        )
    ),
}
