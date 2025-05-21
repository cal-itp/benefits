from datetime import datetime
import hashlib
import hmac
import json
import requests


def _signature_input_string(timestamp, method, request_path, body):
    return f"{timestamp}{method}{request_path}{body}"


def _stp_signature(api_secret, timestamp, method, request_path, body):
    input_string = _signature_input_string(timestamp, method, request_path, body)

    # must encode inputs for hashing, according to https://stackoverflow.com/a/66958131
    byte_key = api_secret.encode("utf-8")
    message = input_string.encode("utf-8")
    stp_signature = hmac.new(byte_key, message, hashlib.sha256).hexdigest()

    return stp_signature


def request_registration(api_url, api_key, api_secret, private_key, client_certificate_file, ca_certificate, timeout):
    registration_path = "/api/v1/registration"
    # eshopResponseMode = "fragment"
    # eshopResponseMode = "query"
    eshopResponseMode = "form_post"
    # eshopResponseMode = "post_message" # don't use
    request_body = {
        "eshopRedirectUrl": "http://localhost:11369/enrollment",
        "mode": "register",
        "eshopResponseMode": eshopResponseMode,
    }
    cert = (client_certificate_file, private_key)
    timestamp = str(int(datetime.now().timestamp()))

    response = requests.post(
        api_url.strip("/") + registration_path,
        json=request_body,
        headers={
            "Content-Type": "application/json",
            "STP-APIKEY": api_key,
            "STP-TIMESTAMP": timestamp,
            "STP-SIGNATURE": _stp_signature(
                api_secret=api_secret,
                timestamp=timestamp,
                method="POST",
                request_path=registration_path,
                body=json.dumps(request_body),
            ),
        },
        cert=cert,
        verify=ca_certificate,
        timeout=timeout,
    )

    response.raise_for_status()

    print(response.status_code)
    print(response.json())
    print(response.json()["gtwUrl"])
    print("<- `" + eshopResponseMode + "`")
