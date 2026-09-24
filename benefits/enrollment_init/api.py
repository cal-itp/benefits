import base64


class Client:
    def __init__(self, api_url, username, password):
        self.api_url = api_url.strip("/")

        encoded_bytes = base64.b64encode(bytes(f"{username}:{password}", "utf-8"))
        self.authorization_header_value = f"Basic {encoded_bytes.decode()}"

    def get_transit_account(self, banking_service_token):
        pass

    def post_cardholder(self, fare_category: int, transit_account_id: int):
        pass
