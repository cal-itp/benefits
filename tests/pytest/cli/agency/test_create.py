import pytest

from django.core.management.base import CommandError

from benefits.cli.agency.create import Create
from benefits.core.models import TransitAgency


@pytest.fixture
def cmd(cmd):
    def call(*args, **kwargs):
        return cmd(Create, *args, **kwargs)

    return call


@pytest.mark.django_db
def test_call_no_slug(cmd):
    with pytest.raises(CommandError, match="the following arguments are required: slug"):
        cmd()


@pytest.mark.django_db
def test_call(cmd, model_TransitProcessor):
    slug = "the-slug"

    agency = TransitAgency.by_slug(slug)
    assert agency is None

    out, err = cmd(slug)

    assert err == ""
    assert "Creating new agency" in out
    assert f"Agency created: {slug}" in out

    agency = TransitAgency.by_slug(slug)
    assert isinstance(agency, TransitAgency)
    assert agency.transit_processor == model_TransitProcessor


@pytest.mark.django_db
def test_call_dupe(cmd):
    slug = "the-slug"

    # first time is OK
    cmd(slug)
    # again with the same slug, not OK
    with pytest.raises(CommandError, match=f"TransitAgency with slug already exists: {slug}"):
        cmd(slug)
