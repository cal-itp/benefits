from django.conf import settings

from eligibility_api.client import Client

from benefits.core import models


def eligibility_from_api(flow: models.EnrollmentFlow, form, agency: models.TransitAgency):
    sub, name = form.cleaned_data.get("sub"), form.cleaned_data.get("name")

    client = Client(
        verify_url=flow.eligibility_api_url,
        headers={flow.eligibility_api_auth_header: flow.eligibility_api_auth_key},
        issuer=settings.ALLOWED_HOSTS[0],
        agency=agency.eligibility_api_id,
        jws_signing_alg=agency.eligibility_api_jws_signing_alg,
        client_private_key=agency.eligibility_api_private_key_data,
        jwe_encryption_alg=flow.eligibility_api_jwe_encryption_alg,
        jwe_cek_enc=flow.eligibility_api_jwe_cek_enc,
        server_public_key=flow.eligibility_api_public_key_data,
        timeout=settings.REQUESTS_TIMEOUT,
    )

    response = client.verify(sub, name, agency.type_names_to_verify(flow))

    if response.error and any(response.error):
        return None
    elif any(response.eligibility):
        return list(response.eligibility)
    else:
        return []


def eligibility_from_oauth(flow: models.EnrollmentFlow, oauth_claim, agency: models.TransitAgency):
    if flow.uses_claims_verification and flow.claims_claim == oauth_claim:
        return agency.type_names_to_verify(flow)
    else:
        return []
