import os
from ConfigParser import RawConfigParser
from cStringIO import StringIO
from base64 import b64encode

with open('resolver.cfg', 'w') as f:
    stream = StringIO()
    config = RawConfigParser()

    config.set('', 'BASE_URL', os.environ.get('BASE_URL'))
    config.set('', 'DATABASE_HOST', 'localhost')
    config.set('', 'DATABASE_USER', 'root')
    config.set('', 'DATABASE_PASS', '')
    config.set('', 'DATABASE_NAME', 'resolver')
    config.set('', 'SECRET_KEY', b64encode(os.urandom(64)))
    config.set('', 'SALT', b64encode(os.urandom(64)))

    config.write(stream)

    stream.seek(0)
    stream.readline() # Skip [DEFAULT]

    for line in stream:
        f.write(line)
