from dataclasses import dataclass

from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy

from benefits.core.context import AgencySlug, SystemName


def _(string, *args, **kwargs):
    """Wraps format_lazy around gettext_lazy for simpler calling."""
    return format_lazy(gettext_lazy(string), *args, **kwargs)


@dataclass
class EnrollmentSuccess:
    success_message: str
    thank_you_message: str


class DefaultEnrollmentSuccess(EnrollmentSuccess):
    def __init__(self, transportation_type):
        super().__init__(
            success_message=_(
                "You were not charged anything today. When boarding {transportation_type}, tap your contactless card and you "
                "will be charged a reduced fare. You will need to re-enroll if you choose to change the card you use to "
                "pay for transit service.",
                transportation_type=transportation_type,
            ),
            thank_you_message=_("Thank you for using Cal-ITP Benefits!"),
        )


class AgencyCardEnrollmentSuccess(EnrollmentSuccess):
    def __init__(self, transit_benefit, transportation_type):
        super().__init__(
            success_message=_(
                "Your contactless card is now enrolled in {transit_benefit}. When boarding {transportation_type}, tap this "
                "card and you will be charged a reduced fare. You will need to re-enroll if you choose to change the card you "
                "use to pay for transit service.",
                transit_benefit=transit_benefit,
                transportation_type=transportation_type,
            ),
            thank_you_message=_("You were not charged anything today. Thank you for using Cal-ITP Benefits!"),
        )


enrollment_success = {
    AgencySlug.CST.value: DefaultEnrollmentSuccess(
        transportation_type=_("a CST bus"),
    ),
    SystemName.AGENCY_CARD.value: AgencyCardEnrollmentSuccess(
        transit_benefit=_("a CST Agency Card transit benefit"), transportation_type=_("a CST bus")
    ),
}
