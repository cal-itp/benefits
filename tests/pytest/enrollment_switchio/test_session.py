from benefits.enrollment_switchio.session import Session


def test_registration_id_default(app_request):
    session = Session(app_request)
    assert session.registration_id is None
