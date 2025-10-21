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

    # to test actually *making* a selection, and validating the form
    # i'm guessing i'd need to figure out how to load a fixture explicitly
    assert len(select.choices) == len(models.TransitAgency.all_active()) + 1

    assert len(form.errors) == 0
    assert form.has_changed() is False
    assert form.is_valid() is False
    assert form.use_custom_validity
