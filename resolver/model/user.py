from hashlib import sha256
from resolver import app
from resolver.database import db

def hash_password(password):
    m = sha256()
    m.update(app.config['SALT'] + password)
    return m.hexdigest()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32))
    password = db.Column(db.String(64))

    def __init__(self, username, password):
        self.username = username
        self.password = hash_password(password)

    def verify_password(self, password):
        return self.password == hash_password(password)

    def change_password(self, password):
        self.password = hash_password(password)
