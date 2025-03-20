from dataclasses import dataclass, asdict
from typing import Optional

from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy

from benefits.core.context import SystemName
from benefits.routes import routes


def _(string, *args, **kwargs):
    """Wraps format_lazy around gettext_lazy for simpler calling."""
    return format_lazy(gettext_lazy(string), *args, **kwargs)


@dataclass
class CTAButton:
    text: str
    route: str
    fallback_text: Optional[str] = None
    extra_classes: Optional[str] = None


@dataclass
class EligibilityStart:
    page_title: str
    headline_text: str
    call_to_action_button: CTAButton
    eligibility_item_template: str = ""

    def dict(self):
        return asdict(self)


class LoginGovEligibilityStart(EligibilityStart):
    def __init__(self, page_title, headline_text):
        super().__init__(
            page_title=page_title,
            headline_text=headline_text,
            call_to_action_button=CTAButton(
                text=_("Get started with"), fallback_text="Login.gov", route=routes.OAUTH_LOGIN, extra_classes="login"
            ),
        )


class AgencyCardEligibilityStart(EligibilityStart):
    def __init__(self, headline_text, eligibility_item_template):
        super().__init__(
            page_title=_("Agency card overview"),
            headline_text=headline_text,
            eligibility_item_template=eligibility_item_template,
            call_to_action_button=CTAButton(text=_("Continue"), route=routes.ELIGIBILITY_CONFIRM),
        )


eligibility_start = {
    SystemName.AGENCY_CARD.value: AgencyCardEligibilityStart(
        headline_text=_("You selected an Agency Card transit benefit."),
        eligibility_item_template="eligibility/includes/eligibility-item--identification--start--cst-agency-card.html",
    ),
    SystemName.CALFRESH.value: LoginGovEligibilityStart(
        page_title=_("CalFresh benefit overview"), headline_text=_("You selected a CalFresh Cardholder transit benefit.")
    ),
    SystemName.COURTESY_CARD.value: AgencyCardEligibilityStart(
        headline_text=_("You selected a Courtesy Card transit benefit."),
        eligibility_item_template="eligibility/includes/eligibility-item--identification--start--mst-agency-card.html",
    ),
    SystemName.MEDICARE.value: EligibilityStart(
        page_title=_("Medicare benefit overview"),
        headline_text=_("You selected a Medicare Cardholder transit benefit."),
        eligibility_item_template="eligibility/includes/eligibility-item--identification--start--medicare.html",
        call_to_action_button=CTAButton(text=_("Continue to Medicare.gov"), route=routes.OAUTH_LOGIN),
    ),
    SystemName.OLDER_ADULT.value: LoginGovEligibilityStart(
        page_title=_("Older Adult benefit overview"),
        headline_text=_("You selected an Older Adult transit benefit."),
    ),
    SystemName.REDUCED_FARE_MOBILITY_ID.value: AgencyCardEligibilityStart(
        headline_text=_("You selected a Reduced Fare Mobility ID transit benefit."),
        eligibility_item_template="eligibility/includes/eligibility-item--identification--start--sbmtd-agency-card.html",
    ),
    SystemName.VETERAN.value: LoginGovEligibilityStart(
        page_title=_("Veterans benefit overview"), headline_text=_("You selected a Veteran transit benefit.")
    ),
}


@dataclass
class EligibilityUnverified:
    headline_text: str
    body_text: str
    button_text: str

    def dict(self):
        return asdict(self)


class AgencyCardEligibilityUnverified(EligibilityUnverified):
    def __init__(self, agency_card):
        super().__init__(
            headline_text=_("Your card information may not have been entered correctly."),
            body_text=_(
                "The number and last name must be entered exactly as they appear on your {agency_card}. "
                "Please check your card and try again, or contact your transit agency for help.",
                agency_card=agency_card,
            ),
            button_text=_("Try again"),
        )


eligibility_unverified = {
    SystemName.AGENCY_CARD.value: AgencyCardEligibilityUnverified(agency_card=_("CST Agency Card")),
    SystemName.COURTESY_CARD.value: AgencyCardEligibilityUnverified(agency_card=_("MST Courtesy Card")),
    SystemName.REDUCED_FARE_MOBILITY_ID.value: AgencyCardEligibilityUnverified(
        agency_card=_("SBMTD Reduced Fare Mobility ID card")
    ),
}
