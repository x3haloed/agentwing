# Relay deployment repository
Resolve settings using `relay/config.py`. The deploy launcher selects a profile;
application defaults are not production truth. Durations in profiles use seconds,
while environment overrides use milliseconds. Deployment documents can be stale.
