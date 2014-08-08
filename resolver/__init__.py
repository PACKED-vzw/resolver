from flask import Flask, render_template
from resolver.exception import NotFoundException

app = Flask(__name__)
app.config.from_object('resolver.config.Config')

# TODO: Logging in production only?
# TODO: Add log file to config

import logging
file_handler = logging.FileHandler("application.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('[%(levelname)s] %(asctime)s -- %(message)s'))
app.logger.addHandler(file_handler)

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
