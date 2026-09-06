import json
from pathlib import Path
def resolve(profile, environ):
    defaults = json.loads(Path("config/defaults.json").read_text())
    defaults.update(json.loads(Path("config/" + profile + ".json").read_text()))
    return {"retry_ms": int(environ.get("RELAY_RETRY_MS", defaults["retry_seconds"] * 1000)),
            "attempts": int(environ.get("RELAY_ATTEMPTS", defaults["attempts"]))}
