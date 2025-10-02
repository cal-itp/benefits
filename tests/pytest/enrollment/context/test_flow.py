import pytest

from benefits.core.context import AgencySlug
from benefits.enrollment import context


@pytest.mark.parametrize("slug", AgencySlug)
def test_enrollent_success(slug):
    assert context.enrollment_success[slug.value]
