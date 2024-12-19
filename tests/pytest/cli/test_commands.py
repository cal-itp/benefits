from dataclasses import dataclass

import pytest

from benefits import VERSION
from benefits.cli.commands import BaseOptions, BenefitsCommand


@dataclass
class MockOptions(BaseOptions):
    str_option: str = ""
    int_option: int = 0


class MockCommand(BenefitsCommand):
    """This is a mock command."""

    name = "mock"
    # needs to be [] for this test to avoid infinite recursion!
    subcommands = []


@pytest.fixture
def with_subcommand():
    # fake a class definition with subcommands
    # using the above MockCommand
    BenefitsCommand.subcommands.append(MockCommand)
    # yield to allow the test to continue
    yield
    # cleanup
    BenefitsCommand.subcommands.clear()


@pytest.fixture
def with_custom_opts():
    # fake the options_cls
    # using the above MockOptions
    BenefitsCommand.options_cls = MockOptions
    # yield to allow the test to continue
    yield
    # cleanup
    BenefitsCommand.options_cls = BaseOptions


@pytest.mark.django_db
def test_class():
    assert BenefitsCommand.help == BenefitsCommand.__doc__
    assert BenefitsCommand.name == "benefits"
    assert BenefitsCommand.options_cls is BaseOptions
    assert BenefitsCommand.subcommands == []
    assert BenefitsCommand.version == VERSION


@pytest.mark.django_db
@pytest.mark.usefixtures("with_subcommand")
def test_subcommands():
    cmd = BenefitsCommand(default_subcmd=MockCommand)

    # it should have parsed cls.subcommands into self.commands
    assert len(cmd.commands) == 1

    # get the subcommand
    subcmd = list(cmd.commands).pop()
    # it should be a MockCommand
    assert isinstance(subcmd, MockCommand)

    # the instance
    assert hasattr(cmd, MockCommand.name)
    assert getattr(cmd, MockCommand.name) == subcmd
    # should have a default_handler
    assert cmd.default_handler == subcmd.handle


@pytest.mark.django_db
def test_init():
    cmd = BenefitsCommand()

    assert cmd.commands == set()
    assert cmd.subparsers == {"benefits": {}}


@pytest.mark.django_db
def test_get_version():
    assert BenefitsCommand().get_version() == VERSION


@pytest.mark.django_db
def test_parse_opts():
    handler = lambda x: x  # noqa: E731
    cmd = BenefitsCommand()
    opts = cmd.parse_opts(handler=handler, skip_checks=True, verbosity=3)

    assert opts.handler == handler
    assert opts.skip_checks
    assert opts.verbosity == 3


@pytest.mark.django_db
@pytest.mark.usefixtures("with_custom_opts")
def test_parse_custom_opts():
    cmd = BenefitsCommand()

    opts = cmd.parse_opts()
    assert isinstance(opts, MockOptions)
    assert opts.str_option == ""
    assert opts.int_option == 0

    opts = cmd.parse_opts(str_option="str", int_option=100)
    assert isinstance(opts, MockOptions)
    assert opts.str_option == "str"
    assert opts.int_option == 100
