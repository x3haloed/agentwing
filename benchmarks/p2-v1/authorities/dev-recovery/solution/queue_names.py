import re
def normalize(value):
 return re.sub(r'[\s-]+','_',value.strip().casefold()).strip('_')
