import os, logging
from pkg_resources import resource_filename
from flask import Flask, render_template
from flask_wtf.csrf import CsrfProtect
from resolver.remoteusermiddleware import RemoteUserMiddleware
from resolver.exception import NotFoundException

app = Flask(__name__)
app.config.from_pyfile('/etc/resolver/resolver.cfg') # TODO replace by resource_string

if os.environ.get('HEROKU', False):
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY',
                                              app.config['SECRET_KEY'])
    app.config['SALT'] = os.environ.get('SALT', app.config['SALT'])

if os.environ.get('HEROKU', False):
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
    return render_template('error.html', title='Page Not Found',
                           message='The page you requested was not found.'), 404

@app.errorhandler(500)
def internal_error(e):
    app.logger.exception(e)
    return render_template('error.html', title='Server Error',
                           message=e), 500

csrf = CsrfProtect()
csrf.init_app(app)

import resolver.controllers

wsgi_app = RemoteUserMiddleware(app.wsgi_app)
