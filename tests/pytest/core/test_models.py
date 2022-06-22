import pytest


@pytest.mark.django_db
def test_EligibilityVerifier_uses_auth_verification_True(first_verifier):
    assert first_verifier.uses_auth_verification


@pytest.mark.django_db
def test_EligibilityVerifier_uses_auth_verification_False(first_verifier):
    first_verifier.auth_provider = None

    assert not first_verifier.uses_auth_verification
