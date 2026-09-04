#!/usr/bin/env python3
"""Execute a command in a new POSIX session so its whole tree can be stopped."""

from __future__ import annotations

import os
import sys


def main() -> int:
    arguments = sys.argv[1:]
    working_directory: str | None = None
    if arguments[:1] == ["--cwd"]:
        if len(arguments) < 3:
            print(f"usage: {sys.argv[0]} [--cwd DIR] -- COMMAND [ARG ...]", file=sys.stderr)
            return 2
        working_directory = arguments[1]
        arguments = arguments[2:]
    if arguments[:1] == ["--"]:
        arguments = arguments[1:]
    if not arguments:
        print(f"usage: {sys.argv[0]} [--cwd DIR] -- COMMAND [ARG ...]", file=sys.stderr)
        return 2
    if working_directory is not None:
        os.chdir(working_directory)
    os.setsid()
    os.execvp(arguments[0], arguments)
    return 127


if __name__ == "__main__":
    raise SystemExit(main())
