"""
The eligibility application: Eligibility Verification API helpers.
"""

from django.conf import settings

from eligibility_api.client import Client

from benefits.core import session


def get_verified_types(request, form):
    """
    Helper calls the eligibility verification API with user input.
    Returns None and updates form with user input error(s).
    Returns a list of verified eligibility types, or an empty list when no types were verified.
    """

    sub, name = form.cleaned_data.get("sub"), form.cleaned_data.get("name")

    agency = session.agency(request)
    verifier = session.verifier(request)

    client = Client(
        verify_url=verifier.api_url,
        headers={verifier.api_auth_header: verifier.api_auth_key},
        issuer=settings.ALLOWED_HOSTS[0],
        agency=agency.agency_id,
        jws_signing_alg=agency.jws_signing_alg,
        client_private_key=agency.private_key_data,
        jwe_encryption_alg=verifier.jwe_encryption_alg,
        jwe_cek_enc=verifier.jwe_cek_enc,
        server_public_key=verifier.public_key_data,
    )

    # get the eligibility type names to check
    types = list(map(lambda t: t.name, agency.types_to_verify(verifier)))

    response = client.verify(sub, name, types)

    if response.error and any(response.error):
        form.add_api_errors(response.error)
        return None
    elif any(response.eligibility):
        return list(response.eligibility)
    else:
        return []
