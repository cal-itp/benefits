import pytest

from benefits.core import context as core_context
from benefits.eligibility import context as eligibility_context


@pytest.mark.parametrize("system_name", core_context.SystemName)
def test_eligibility_start(system_name):
    assert eligibility_context.eligibility_start[system_name.value]
