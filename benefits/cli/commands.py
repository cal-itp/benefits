from dataclasses import dataclass
from typing import Callable

from django.core.management.base import BaseCommand

from benefits import VERSION


@dataclass
class BaseOptions:
    handler: Callable = None
    skip_checks: bool = False
    verbosity: int = 1


class BenefitsCommand(BaseCommand):
    """Base class for Benefits CLI commands."""

    name = "benefits"
    help = __doc__
    options_cls = BaseOptions
    subcommands = []
    version = VERSION

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False, default_subcmd=None):
        super().__init__(stdout, stderr, no_color, force_color)

        self.commands = set()
        # for each subcommand declared on the BenefitsCommand class (or subclass)
        # instantiate it and add it to the commands set
        self.commands.update(cmd(stdout, stderr, no_color, force_color) for cmd in self.subcommands)
        # set an attribute on this instance for each command
        for cmd in self.commands:
            setattr(self, cmd.name, cmd)
        # can be used by subclasses to track their own argument subparsers
        self.subparsers = {self.name: {}}

        # default_subcmd should be one of the items in BenefitsCommand.subcommands (or subclass.subcommands)
        # i.e. a class that implements one of the subcommands for this BenefitsCommand (or subclass)
        if default_subcmd:
            if default_subcmd in self.subcommands:
                # we want to store the handle method for the instance of this default_subcmd class
                # read command attribute created above
                # the default handler is a function to call when the command is called without a subcommand
                self.default_handler = getattr(self, default_subcmd.name).handle
            else:
                raise ValueError("default_subcmd must be in this Command's declared subcommands list.")
        else:
            self.default_handler = None

    @property
    def subparser(self):
        """Gets the single self.subparsers with a name matching this command's."""
        return self.subparsers[self.name]

    def add_arguments(self, parser):
        """Entry point for subclassed commands to add custom arguments."""
        if len(self.commands) < 1:
            return

        # For each command this BenefitsCommand instance defines
        # create an argparse subparser for that command's arguments
        # adapted from https://adamj.eu/tech/2024/08/14/django-management-command-sub-commands/
        command_required = self.default_handler is None
        subparsers = parser.add_subparsers(title="commands", required=command_required)

        for command in self.commands:
            subparser = subparsers.add_parser(command.name, help=command.help)
            # command is an instance inheriting from BenefitsCommand
            # so it has an .add_arguments() method
            # add them to the command's subparser
            command.add_arguments(subparser)
            # set_defaults makes the resulting "handler" argument equal to the
            # command's handle function
            subparser.set_defaults(handler=command.handle)
            # store a reference to each command subparser
            self.subparser[command.name] = subparser

    def get_version(self) -> str:
        """Override `BaseCommand.get_version()` to return the `benefits` version."""
        return self.version

    def handle(self, *args, **options):
        """The actual logic of the command. Subclasses of Django's `BaseCommand` must implement this method.

        The default implementation for `BenefitsCommands` implements a pattern like:

        ```
        command --cmd-opt subcommand --subcmd-opt subcmd_arg
        ```

        Subclasses of `BenefitsCommand` may provide a custom implementation as-needed.
        """
        # by default, parse options as a BaseOptions instance
        opts = self.parse_opts(**options)
        # get the handler parsed from the options, or the default_handler
        handler = opts.handler or self.default_handler

        if handler:
            if opts.verbosity > 1:
                # handler is a class method, use its __self__ prop to get back to the instance
                command_name = handler.__self__.name
                self.stdout.write(self.style.WARNING(f"command: {command_name}"))
            # call it
            handler(*args, **options)

    def parse_opts(self, **options):
        """Parse options into a dataclass instance."""
        options = {k: v for k, v in options.items() if k in dir(self.options_cls)}
        return self.options_cls(**options)
