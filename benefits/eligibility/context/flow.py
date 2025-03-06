from dataclasses import dataclass


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
