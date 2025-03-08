import pytest

from benefits.core import context as core_context
from benefits.eligibility import context as eligibility_context


@pytest.mark.parametrize("slug", core_context.AgencySlug)
def test_eligibility_index(slug):
    assert eligibility_context.eligibility_index[slug.value]
