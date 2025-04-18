import pytest

from benefits.core import context as core_context


@pytest.mark.parametrize("slug", core_context.AgencySlug)
def test_agency_index(slug):
    assert core_context.agency_index[slug.value]
