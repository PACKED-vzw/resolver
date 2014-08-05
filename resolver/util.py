from flask import session
from resolver import app

def log(action):
    app.logger.info("Resolver: user `%s' %s", session.get('username'), action)
