#!/usr/bin/env python
"""Benefits command-line utility for administrative tasks."""
import os
import sys

from django.core.management import execute_from_command_line

from benefits import VERSION


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "benefits.settings")

    if len(sys.argv) == 2 and sys.argv[1] == "--version":
        print(f"benefits, {VERSION}")

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
