import pytest

from benefits.core.models import EligibilityType, EligibilityVerifier


@pytest.mark.django_db
def test_EligibilityType_get_matching(model_EligibilityType):
    eligibility = EligibilityType.get(model_EligibilityType.id)

    assert eligibility == model_EligibilityType


@pytest.mark.django_db
def test_EligibilityType_get_nonmatching():
    with pytest.raises(EligibilityType.DoesNotExist):
        EligibilityType.get(99999)


@pytest.mark.django_db
def test_EligibilityType_get_many_matching(model_EligibilityType):
    new_type = EligibilityType.get(model_EligibilityType.id)
    new_type.pk = None
    new_type.save()

    result = EligibilityType.get_many([model_EligibilityType.id, new_type.id])

    assert len(result) == 2
    assert model_EligibilityType in result
    assert new_type in result


@pytest.mark.django_db
def test_EligibilityType_get_many_nonmatching():
    result = EligibilityType.get_many([99998, 99999])

    assert len(result) == 0


@pytest.mark.django_db
def test_EligibilityType_get_many_somematching(model_EligibilityType):
    result = EligibilityType.get_many([model_EligibilityType.id, 99999])

    assert len(result) == 1
    assert model_EligibilityType in result


@pytest.mark.django_db
def test_EligibilityVerifier_by_id_matching(model_EligibilityVerifier):
    verifier = EligibilityVerifier.by_id(model_EligibilityVerifier.id)

    assert verifier == model_EligibilityVerifier


@pytest.mark.django_db
def test_EligibilityVerifier_by_id_nonmatching():
    with pytest.raises(EligibilityVerifier.DoesNotExist):
        EligibilityVerifier.by_id(99999)


@pytest.mark.django_db
def test_EligibilityVerifier_with_AuthProvider_with_verification(
    model_EligibilityVerifier, model_AuthProvider_with_verification
):
    model_EligibilityVerifier.auth_provider = model_AuthProvider_with_verification

    assert model_EligibilityVerifier.is_auth_required
    assert model_EligibilityVerifier.uses_auth_verification


@pytest.mark.django_db
def test_EligibilityVerifier_with_AuthProvider_without_verification(
    model_EligibilityVerifier, model_AuthProvider_without_verification
):
    model_EligibilityVerifier.auth_provider = model_AuthProvider_without_verification

    assert model_EligibilityVerifier.is_auth_required
    assert not model_EligibilityVerifier.uses_auth_verification


@pytest.mark.django_db
def test_EligibilityVerifier_without_AuthProvider(model_EligibilityVerifier):
    model_EligibilityVerifier.auth_provider = None

    assert not model_EligibilityVerifier.is_auth_required
    assert not model_EligibilityVerifier.uses_auth_verification


@pytest.mark.django_db
def test_TransitAgency_get_type_id_matching(model_TransitAgency):
    eligibility = model_TransitAgency.eligibility_types.first()
    result = model_TransitAgency.get_type_id(eligibility.name)

    assert result == eligibility.id


@pytest.mark.django_db
def test_TransitAgency_get_type_id_manymatching(model_TransitAgency):
    eligibility = model_TransitAgency.eligibility_types.first()
    new_eligibility = EligibilityType.get(eligibility.id)
    new_eligibility.pk = None
    new_eligibility.save()
    model_TransitAgency.eligibility_types.add(new_eligibility)

    with pytest.raises(Exception, match=r"name"):
        model_TransitAgency.get_type_id(eligibility.name)


@pytest.mark.django_db
def test_TransitAgency_get_type_id_nonmatching(model_TransitAgency):
    with pytest.raises(Exception, match=r"name"):
        model_TransitAgency.get_type_id("something")


@pytest.mark.django_db
def test_TransitAgency_supports_type_matching(model_TransitAgency):
    eligibility = model_TransitAgency.eligibility_types.first()

    assert model_TransitAgency.supports_type(eligibility)


@pytest.mark.django_db
def test_TransitAgency_supports_type_nonmatching(model_TransitAgency):
    eligibility = model_TransitAgency.eligibility_types.first()
    new_eligibility = EligibilityType.get(eligibility.id)
    new_eligibility.pk = None
    new_eligibility.save()

    assert not model_TransitAgency.supports_type(new_eligibility)


@pytest.mark.django_db
def test_TransitAgency_supports_type_wrongtype(model_TransitAgency):
    eligibility = model_TransitAgency.eligibility_types.first()

    assert not model_TransitAgency.supports_type(eligibility.name)


@pytest.mark.django_db
def test_TransitAgency_index_url(model_TransitAgency):
    result = model_TransitAgency.index_url

    assert result.endswith(model_TransitAgency.slug)
