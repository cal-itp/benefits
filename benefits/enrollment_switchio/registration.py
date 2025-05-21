from datetime import datetime
import hashlib
import hmac
import json
import os
import requests

api_url = os.environ.get("SWITCHIO_API_URL")
api_key = os.environ.get("SWITCHIO_API_KEY")
api_secret = os.environ.get("SWITCHIO_API_SECRET")
private_key = os.path.abspath(os.environ.get("SWITCHIO_PRIVATE_KEY_PATH"))
client_certificate_file = os.path.abspath(os.environ.get("SWITCHIO_CLIENT_CERT_PATH"))
ca_certificate = os.path.abspath(os.environ.get("SWITCHIO_CA_CERT_PATH"))

timestamp = str(int(datetime.now().timestamp()))


def get_input_string(timestamp, method, request_path, body):
    return f"{timestamp}{method}{request_path}{body}"


def stp_signature(api_secret, timestamp, method, request_path, body):
    input_string = get_input_string(timestamp, method, request_path, body)

    # https://stackoverflow.com/a/66958131
    byte_key = api_secret.encode("utf-8")
    message = input_string.encode("utf-8")
    stp_signature = hmac.new(byte_key, message, hashlib.sha256).hexdigest()

    return stp_signature


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

response = requests.post(
    api_url.strip("/") + registration_path,
    json=request_body,
    headers={
        "Content-Type": "application/json",
        "STP-APIKEY": api_key,
        "STP-TIMESTAMP": timestamp,
        "STP-SIGNATURE": stp_signature(
            api_secret=api_secret,
            timestamp=timestamp,
            method="POST",
            request_path=registration_path,
            body=json.dumps(request_body),
        ),
    },
    cert=cert,
    verify=ca_certificate,
    timeout=5,
)

response.raise_for_status()

print(response.status_code)
print(response.json())
print(response.json()["gtwUrl"])
print("<- `" + eshopResponseMode + "`")
