#!/usr/bin/env python3
"""Wait for a Swiftlet terminal metric after a recorded server-log boundary."""

import argparse
import re
import time
from pathlib import Path


TERMINAL = re.compile(
    r"^\[chatcmpl-[^]]+\] \d+ prompt \+ \d+ reused "
    r"\(\d+ prefix matched\) \+ \d+ generated, "
    r"ttft \d+(?:\.\d+)?s, \d+(?:\.\d+)? tok/s$"
)


def wait_for_terminal(path, after_lines, timeout=30, interval=0.5):
    deadline = time.monotonic() + timeout
    while True:
        # Ignore a partial final write; only a complete metric is a barrier.
        lines = path.read_text().splitlines(keepends=True)
        if any(line.endswith("\n") and TERMINAL.fullmatch(line.rstrip("\n"))
               for line in lines[after_lines:]):
            return True
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return False
        time.sleep(min(interval, remaining))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    parser.add_argument("after_lines", type=int)
    args = parser.parse_args()
    if args.after_lines < 0:
        parser.error("after_lines must be nonnegative")
    raise SystemExit(0 if wait_for_terminal(args.log, args.after_lines) else 1)
