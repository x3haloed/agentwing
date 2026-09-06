from .rules import SECRET_KEYS
def clean(value):
 return {k:'[REDACTED]' if k in SECRET_KEYS else v for k,v in value.items()}
