from archive.factory import backend
def persist(payload):
 return backend().write(payload)
