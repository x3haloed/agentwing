#!/bin/sh
. deploy/active.env
export RELAY_PROFILE RELAY_RETRY_MS RELAY_ATTEMPTS
exec python3 -m relay.main
