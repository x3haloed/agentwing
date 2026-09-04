#!/bin/sh
set -eu
result=$(/usr/bin/python3 -c 'from app import normalize; print(normalize("  Agent Wing  "))')
test "$result" = "agent-wing"
