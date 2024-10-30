import pytest

from benefits import VERSION
from benefits.cli.commands import BaseOptions, BenefitsCommand


@pytest.fixture
def benefits_cmd():
    return BenefitsCommand()


@pytest.mark.django_db
def test_BenefitsCommand_init(benefits_cmd):
    assert benefits_cmd.name == "benefits"
    assert benefits_cmd.help == BenefitsCommand.__doc__
    assert benefits_cmd.options_cls == BaseOptions
    assert benefits_cmd.version == VERSION


@pytest.mark.django_db
def test_BenefitsCommand_get_version(benefits_cmd):
    assert benefits_cmd.get_version() == VERSION


@pytest.mark.django_db
def test_BenefitsCommand_parse_opts(benefits_cmd):
    opts = benefits_cmd.parse_opts(skip_checks=True, verbosity=3)

    assert opts.skip_checks
    assert opts.verbosity == 3
