from django.conf import settings
from eligibility_api.client import Client

from benefits.core import models


def eligibility_from_api(flow: models.EnrollmentFlow, form, agency: models.TransitAgency):
    sub, name = form.cleaned_data.get("sub"), form.cleaned_data.get("name")

    client = Client(
        verify_url=flow.api_request.api_url,
        headers={flow.api_request.api_auth_header: flow.api_request.api_auth_key},
        issuer=settings.ALLOWED_HOSTS[0],
        agency=agency.eligibility_api_config.api_id,
        jws_signing_alg=flow.api_request.api_jws_signing_alg,
        client_private_key=flow.api_request.api_client_private_key_data,
        jwe_encryption_alg=flow.api_request.api_jwe_encryption_alg,
        jwe_cek_enc=flow.api_request.api_jwe_cek_enc,
        server_public_key=flow.api_request.api_public_key_data,
        timeout=settings.REQUESTS_TIMEOUT,
    )

    response = client.verify(sub, name, [flow.system_name])

    if response.error and any(response.error):
        return None
    # response.eligibility is a single item list containing the type of eligibility we are trying to verify, e.g. ["senior"]
    elif flow.system_name in response.eligibility:
        return True
    else:
        return False
