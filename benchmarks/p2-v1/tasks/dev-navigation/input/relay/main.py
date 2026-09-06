import os
from relay.config import resolve
print(resolve(os.environ["RELAY_PROFILE"], os.environ))
