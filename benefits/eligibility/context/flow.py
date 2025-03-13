from dataclasses import dataclass
from typing import Optional

from django.utils.translation import gettext_lazy as _

from benefits.core.context import SystemName
from benefits.routes import routes


@dataclass
class CTAButton:
    text: str
    route: str
    fallback_text: Optional[str] = None


@dataclass
class EligibilityStart:
    page_title: str
    headline_text: str
    eligibility_item_template: str
    call_to_action_button: CTAButton


eligibility_start = {
    SystemName.AGENCY_CARD.value: EligibilityStart(
        page_title=_("Agency card overview"),
        headline_text=_("You selected an Agency Card transit benefit."),
        eligibility_item_template="eligibility/includes/eligibility-item--identification--start--cst-agency-card.html",
        call_to_action_button=CTAButton(text=_("Continue"), route=routes.ELIGIBILITY_CONFIRM),
    ),
    SystemName.CALFRESH.value: EligibilityStart(
        page_title=_("CalFresh benefit overview"),
        headline_text=_("You selected a CalFresh Cardholder transit benefit."),
        eligibility_item_template="eligibility/includes/eligibility-item--identification--start--login-gov.html",
        call_to_action_button=CTAButton(text=_("Get started with"), fallback_text="Login.gov", route=routes.OAUTH_LOGIN),
    ),
    SystemName.COURTESY_CARD.value: EligibilityStart(
        page_title=_("Agency card overview"),
        headline_text=_("You selected a Courtesy Card transit benefit."),
        eligibility_item_template="eligibility/includes/eligibility-item--identification--start--mst-agency-card.html",
        call_to_action_button=CTAButton(text=_("Continue"), route=routes.ELIGIBILITY_CONFIRM),
    ),
    SystemName.MEDICARE.value: EligibilityStart(
        page_title=_("Medicare benefit overview"),
        headline_text=_("You selected a Medicare Cardholder transit benefit."),
        eligibility_item_template="eligibility/includes/eligibility-item--identification--start--medicare.html",
        call_to_action_button=CTAButton(text=_("Continue to Medicare.gov"), route=routes.OAUTH_LOGIN),
    ),
    SystemName.OLDER_ADULT.value: EligibilityStart(
        page_title=_("Older Adult benefit overview"),
        headline_text=_("You selected an Older Adult transit benefit."),
        eligibility_item_template="eligibility/includes/eligibility-item--identification--start--login-gov.html",
        call_to_action_button=CTAButton(text=_("Get started with"), fallback_text="Login.gov", route=routes.OAUTH_LOGIN),
    ),
    SystemName.REDUCED_FARE_MOBILITY_ID.value: EligibilityStart(
        page_title=_("Agency card overview"),
        headline_text=_("You selected a Reduced Fare Mobility ID transit benefit."),
        eligibility_item_template="eligibility/includes/eligibility-item--identification--start--sbmtd-agency-card.html",
        call_to_action_button=CTAButton(text=_("Continue"), route=routes.ELIGIBILITY_CONFIRM),
    ),
    SystemName.VETERAN.value: EligibilityStart(
        page_title=_("Veterans benefit overview"),
        headline_text=_("You selected a Veteran transit benefit."),
        eligibility_item_template="eligibility/includes/eligibility-item--identification--start--login-gov.html",
        call_to_action_button=CTAButton(text=_("Get started with"), fallback_text="Login.gov", route=routes.OAUTH_LOGIN),
    ),
}
