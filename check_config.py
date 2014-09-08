import os
from base64 import b64encode
config = """BASE_URL = "%s"

DATABASE_HOST = "localhost"
DATABASE_USER = "root"
DATABASE_PASS = ""
DATABASE_NAME = "resolver"

SECRET_KEY = "%s"
SALT = "%s"
""" % (os.environ.get('BASE_URL'),
       b64encode(os.urandom(64)),
       b64encode(os.urandom(64)))

with open('resolver.cfg', 'w') as f:
    f.write(config)
