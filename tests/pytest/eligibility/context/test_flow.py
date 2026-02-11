import pytest

from benefits.core import context as core_context
from benefits.eligibility import context as eligibility_context
from benefits.eligibility.context.flow import EligibilityUnverified


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
