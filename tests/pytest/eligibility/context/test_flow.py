import pytest

from benefits.core import context as core_context
from benefits.routes import routes
from benefits.eligibility import context as eligibility_context
from benefits.eligibility.context.flow import CTAButton, EligibilityStart, EligibilityUnverified


@pytest.mark.parametrize("system_name", core_context.SystemName)
def test_eligibility_start(system_name):
    assert eligibility_context.eligibility_start[system_name.value]


def test_EligibilityStart_dict():
    context_object = EligibilityStart(
        page_title="Test page title",
        headline_text="This is a headline.",
        eligibility_item_headline="Item headline",
        eligibility_item_body="Item body",
        call_to_action_button=CTAButton(text="button text", route=routes.INDEX),
    )

    context_dict = context_object.dict()

    assert isinstance(context_dict, dict)


@pytest.mark.parametrize(
    "system_name",
    [
        core_context.SystemName.AGENCY_CARD,
        core_context.SystemName.COURTESY_CARD,
        core_context.SystemName.REDUCED_FARE_MOBILITY_ID,
    ],
)
def test_eligibility_unverified(system_name):
    assert eligibility_context.eligibility_unverified[system_name.value]


def test_EligibilityUnverified_dict():
    context_object = EligibilityUnverified(
        headline_text="This is a headline",
        body_text="This is the body text",
        button_text="Button",
    )

    context_dict = context_object.dict()

    assert isinstance(context_dict, dict)
