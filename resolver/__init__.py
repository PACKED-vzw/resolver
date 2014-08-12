import logging
from flask import Flask, render_template
from resolver.remoteusermiddleware import RemoteUserMiddleware
from resolver.exception import NotFoundException

app = Flask(__name__)
app.config.from_object('resolver.config.Config')
app.config.from_envvar('RESOLVER_SETTINGS', silent=True)

# TODO: Logging in production only?
# TODO: Add log file to config
if os.environ.get('HEROKU') == 1:
    import sys
    handler = logging.StreamHandler(sys.stdout)
else:
    handler = logging.FileHandler("application.log")

handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('[%(levelname)s] %(asctime)s -- %(message)s'))
app.logger.addHandler(handler)

@app.errorhandler(404)
@app.errorhandler(NotFoundException)
def page_not_found(e):
    return render_template('notice.html', title='Page Not Found',
                           message='The page you requested was not found.'), 404

@app.errorhandler(500)
def internal_error(e):
    app.logger.exception(e)
    return render_template('notice.html', title='Server Error',
                           message='Something went terribly wrong!'), 500

import resolver.controllers

wsgi_app = RemoteUserMiddleware(app.wsgi_app)
