import pytest

from django.core.management import call_command


@pytest.fixture
def cmd(capfd):
    def call(cls, *args, **kwargs):
        call_command(cls(), *args, **kwargs)
        return capfd.readouterr()

    return call
