import pytest

from benefits.cli.agency.list import List
from benefits.cli.management.commands.agency import Command


@pytest.mark.django_db
def test_class():
    assert Command.help == Command.__doc__
    assert Command.name == "agency"
    assert Command.subcommands == [List]


@pytest.mark.django_db
def test_init():
    cmd = Command()

    assert "agency" in cmd.subparsers
    assert cmd.subparser == cmd.subparsers["agency"]

    list_cmd = getattr(cmd, "list")
    assert isinstance(list_cmd, List)
    assert cmd.default_handler == list_cmd.handle
