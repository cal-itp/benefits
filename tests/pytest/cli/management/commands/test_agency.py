import pytest

from benefits.cli.agency.create import Create
from benefits.cli.agency.list import List
from benefits.cli.management.commands.agency import Command


@pytest.fixture
def cmd(cmd):
    def call(*args, **kwargs):
        return cmd(Command, *args, **kwargs)

    return call


@pytest.mark.django_db
def test_class():
    assert Command.help == Command.__doc__
    assert Command.name == "agency"

    assert List in Command.subcommands
    assert Create in Command.subcommands


@pytest.mark.django_db
def test_init():
    cmd = Command()

    assert "agency" in cmd.subparsers
    assert cmd.subparser == cmd.subparsers["agency"]

    list_cmd = getattr(cmd, "list")
    assert isinstance(list_cmd, List)
    assert cmd.default_handler == list_cmd.handle


@pytest.mark.django_db
def test_call(cmd):
    out, err = cmd()

    assert "No matching agencies" in out
    assert err == ""
