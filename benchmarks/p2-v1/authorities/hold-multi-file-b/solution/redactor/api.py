from .rules import SECRET_KEYS
def clean(value):
 if isinstance(value,dict):return {k:'[REDACTED]' if k.casefold() in SECRET_KEYS else clean(v) for k,v in value.items()}
 if isinstance(value,list):return [clean(v) for v in value]
 return value
