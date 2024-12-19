import pytest

from benefits.cli.agency.list import List


@pytest.fixture
def cmd(cmd):
    def call(*args, **kwargs):
        return cmd(List, *args, **kwargs)

    return call


@pytest.mark.django_db
def test_call(cmd):
    out, err = cmd()

    assert err == ""
    assert "No matching agencies" in out


@pytest.mark.django_db
def test_call_one_agency(cmd, model_TransitAgency):
    out, err = cmd()

    assert err == ""
    assert "1 agency" in out
    assert str(model_TransitAgency) in out


@pytest.mark.django_db
def test_call_multiple_agencies(cmd, model_TransitAgency):
    orig_agency = str(model_TransitAgency)

    model_TransitAgency.pk = None
    model_TransitAgency.long_name = "Another agency"
    model_TransitAgency.save()

    out, err = cmd()

    assert err == ""
    assert "2 agencies" in out
    assert orig_agency in out
    assert str(model_TransitAgency) in out


@pytest.mark.django_db
def test_call_active(cmd, model_TransitAgency):
    orig_agency = str(model_TransitAgency)

    model_TransitAgency.pk = None
    model_TransitAgency.long_name = "Another agency"
    model_TransitAgency.active = False
    model_TransitAgency.save()

    out, err = cmd()

    assert err == ""
    assert "1 agency" in out
    assert orig_agency in out
    assert str(model_TransitAgency) not in out

    out, err = cmd("--all")

    assert err == ""
    assert "2 agencies" in out
    assert orig_agency in out
    assert f"[inactive] {model_TransitAgency}" in out
