import pytest


@pytest.fixture(scope="session")
def django_db_setup():
    # use existing database since it's read-only
    pass
