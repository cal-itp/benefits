import pytest


@pytest.mark.django_db
def test_EligibilityVerifier_with_auth_verification(model_EligibilityVerifier, model_AuthProvider_with_verification):
    model_EligibilityVerifier.auth_provider = model_AuthProvider_with_verification

    assert model_EligibilityVerifier.uses_auth_verification


@pytest.mark.django_db
def test_EligibilityVerifier_without_auth_verification(model_EligibilityVerifier, model_AuthProvider_without_verification):
    model_EligibilityVerifier.auth_provider = model_AuthProvider_without_verification

    assert not model_EligibilityVerifier.uses_auth_verification


@pytest.mark.django_db
def test_EligibilityVerifier_without_AuthProvider(model_EligibilityVerifier):
    model_EligibilityVerifier.auth_provider = None

    assert not model_EligibilityVerifier.uses_auth_verification
