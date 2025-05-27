import os

from benefits.enrollment_switchio import registration


def _get_env_values():
    return dict(
        api_url=os.environ.get("SWITCHIO_API_URL"),
        api_key=os.environ.get("SWITCHIO_API_KEY"),
        api_secret=os.environ.get("SWITCHIO_API_SECRET"),
        # these paths are relative to the working directory from which you are running this file.
        private_key=os.path.abspath(os.environ.get("SWITCHIO_PRIVATE_KEY_PATH")),
        client_certificate_file=os.path.abspath(os.environ.get("SWITCHIO_CLIENT_CERT_PATH")),
        ca_certificate=os.path.abspath(os.environ.get("SWITCHIO_CA_CERT_PATH")),
    )


if __name__ == "__main__":
    values = _get_env_values()
    client = registration.Client(**values)

    response = client.request_registration(eshopResponseMode=registration.EShopResponseMode.FORM_POST)

    print(response)
