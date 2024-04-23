from benefits.eligibility.forms import MSTCourtesyCard, SBMTDMobilityPass


def test_MSTCourtesyCard():
    form = MSTCourtesyCard(data={"sub": "12345", "name": "Gonzalez"})

    assert form.is_valid()


def test_SBMTDMobilityPass():
    form = SBMTDMobilityPass(data={"sub": "1234", "name": "Barbara"})

    assert form.is_valid()
