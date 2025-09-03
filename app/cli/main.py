"""Internal entrypoint for accessing certain app features from the CLI.

This package is an internal utility that we use to programmatically access
certain features of our app without needing to initialize a full Flask
application context. (The latter would be quite cumbersome and slow.)

The structure of the CLI interface is deliberately minimal, as we don’t expose
it to end-users directly, but if at all only via dedicated wrapper scripts.
"""

import sys

import cli.commands  # noqa: F401
import cli.registry


def main():
    if len(sys.argv) < 2:
        print('Missing required subcommand!', file=sys.stderr)
        sys.exit(1)

    try:
        command = cli.registry.COMMANDS[sys.argv[1]]
    except KeyError:
        print('No such subcommand!', file=sys.stderr)
        sys.exit(1)

    command(sys.argv[1:])


if __name__ == '__main__':
    main()
