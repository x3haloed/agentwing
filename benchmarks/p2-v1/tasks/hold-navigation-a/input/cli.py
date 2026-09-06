from archive.commands import REGISTRY,ALIASES
def run(command,payload):
 while command in ALIASES:command=ALIASES[command]
 return REGISTRY[command](payload)
