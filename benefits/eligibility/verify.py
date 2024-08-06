from django.conf import settings

from eligibility_api.client import Client


def eligibility_from_api(verifier, form, agency):
    sub, name = form.cleaned_data.get("sub"), form.cleaned_data.get("name")

    client = Client(
        verify_url=verifier.eligibility_api_url,
        headers={verifier.eligibility_api_auth_header: verifier.eligibility_api_auth_key},
        issuer=settings.ALLOWED_HOSTS[0],
        agency=agency.agency_id,
        jws_signing_alg=agency.jws_signing_alg,
        client_private_key=agency.private_key_data,
        jwe_encryption_alg=verifier.eligibility_api_jwe_encryption_alg,
        jwe_cek_enc=verifier.eligibility_api_jwe_cek_enc,
        server_public_key=verifier.eligibility_api_public_key_data,
        timeout=settings.REQUESTS_TIMEOUT,
    )

    response = client.verify(sub, name, agency.type_names_to_verify(verifier))

    if response.error and any(response.error):
        return None
    elif any(response.eligibility):
        return list(response.eligibility)
    else:
        return []


def eligibility_from_oauth(verifier, oauth_claim, agency):
    if verifier.uses_claims_verification and verifier.claims_provider.claim == oauth_claim:
        return agency.type_names_to_verify(verifier)
    else:
        return []
