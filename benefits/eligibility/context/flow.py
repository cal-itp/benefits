from dataclasses import dataclass

from django.utils.translation import gettext_lazy as _

from benefits.core.context import SystemName
from benefits.routes import routes


@dataclass
class CTAButton:
    text: str
    fallback_text: str
    route: str


@dataclass
class EligibilityStart:
    page_title: str
    headline_text: str
    eligibility_item_template: str
    call_to_action_button: CTAButton


eligibility_start = {
    SystemName.AGENCY_CARD.value: EligibilityStart(),
    SystemName.CALFRESH.value: EligibilityStart(
        page_title=_("CalFresh benefit overview"),
        headline_text=_("You selected a CalFresh Cardholder transit benefit."),
        eligibility_item_template="eligibility/includes/eligibility-item--identification--start--login-gov.html",
        call_to_action_button=CTAButton(text="Get started with", fallback_text="Login.gov", route=routes.OAUTH_LOGIN),
    ),
}
