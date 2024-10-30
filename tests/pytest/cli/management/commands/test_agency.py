import pytest

from benefits.cli.management.commands.agency import Command


@pytest.mark.django_db
def test_class():
    assert Command.help == Command.__doc__
    assert Command.name == "agency"
    assert Command.subcommands == []


@pytest.mark.django_db
def test_init():
    cmd = Command()

    assert "agency" in cmd.subparsers
    assert cmd.subparser == cmd.subparsers["agency"]
