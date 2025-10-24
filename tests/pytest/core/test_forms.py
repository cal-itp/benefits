import pytest

from benefits.core import models
from benefits.core.forms import ChooseAgencyForm


@pytest.mark.django_db
def test_ChooseAgencyForm():
    form = ChooseAgencyForm()
    select = form.fields["select_transit_agency"]

    assert select.initial is None
    assert select.required
    assert select.widget.attrs["aria-label"]
    assert select.widget.attrs["class"] == "form-select"

    assert len(select.choices) == len(models.TransitAgency.all_active()) + 1
    assert len(form.errors) == 0
    assert not form.has_changed()
    assert not form.is_valid()
    assert form.use_custom_validity


@pytest.mark.django_db
def test_ChooseAgencyForm_hydrated(model_TransitAgency):
    form = ChooseAgencyForm({"select_transit_agency": model_TransitAgency.slug})
    assert form.has_changed()
    assert form.is_valid()


@pytest.mark.django_db
def test_ChooseAgencyForm_invalid():
    form = ChooseAgencyForm({"select_transit_agency": "invalid"})
    with pytest.raises(Exception, match=r"object has no attribute 'cleaned_data'"):
        form.clean()
