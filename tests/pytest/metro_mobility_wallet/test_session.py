from benefits.metro_mobility_wallet.session import Session


class TestSession:
    def test_init(self):
        session = Session()
        assert session
