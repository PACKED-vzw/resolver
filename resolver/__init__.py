from flask import Flask
from config import Config

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

from resolver.controllers import *
