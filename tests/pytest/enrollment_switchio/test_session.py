from benefits.enrollment_switchio.session import Session


def test_Session_defaults(app_request):
    session = Session(app_request)
    assert session.registration_id is None
    assert session.gateway_url is None


def test_registration_id(app_request):
    session = Session(app_request)
    session.registration_id = "123abc"

    assert session.registration_id == "123abc"


def test_gateway_url(app_request):
    session = Session(app_request)
    gateway_url = "https://example.com"
    session.gateway_url = gateway_url

    assert session.gateway_url == gateway_url
