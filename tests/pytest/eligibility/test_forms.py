from benefits.eligibility.forms import MSTCourtesyCard, SBMTDMobilityPass


def test_MSTCourtesyCard():
    form = MSTCourtesyCard(data={"sub": "12345", "name": "Gonzalez"})

    assert form.is_valid()

    sub_attrs = form.fields["sub"].widget.attrs
    assert sub_attrs["pattern"] == r"\d{5}"
    assert sub_attrs["inputmode"] == "numeric"
    assert sub_attrs["maxlength"] == 5
    assert sub_attrs["data-custom-validity"] == "Please enter a 5-digit number."

    name_attrs = form.fields["name"].widget.attrs
    assert name_attrs["maxlength"] == 255
    assert name_attrs["data-custom-validity"] == "Please enter your last name."


def test_SBMTDMobilityPass():
    form = SBMTDMobilityPass(data={"sub": "1234", "name": "Barbara"})

    assert form.is_valid()

    sub_attrs = form.fields["sub"].widget.attrs
    assert sub_attrs["pattern"] == r"\d{4}"
    assert sub_attrs["maxlength"] == 4
    assert sub_attrs["inputmode"] == "numeric"
    assert sub_attrs["data-custom-validity"] == "Please enter a 4-digit number."

    name_attrs = form.fields["name"].widget.attrs
    assert name_attrs["maxlength"] == 255
    assert name_attrs["data-custom-validity"] == "Please enter your last name."
