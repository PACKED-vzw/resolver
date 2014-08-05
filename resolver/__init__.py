from flask import Flask
from config import Config

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# TODO: Logging in production only
# TODO: Add log file to config

import logging
file_handler = logging.FileHandler("application.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('[%(levelname)s] %(asctime)s -- %(message)s'))
app.logger.addHandler(file_handler)

import resolver.controllers
