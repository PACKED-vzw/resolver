from resolver import app
from resolver.database import db
from passlib.context import CryptContext
from flask.ext.login import make_secure_token

pwd_context = CryptContext(schemes=["pbkdf2_sha512", "sha512_crypt", "bcrypt"], default="pbkdf2_sha512")


def hash_password(password):
    return pwd_context.encrypt(password)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(256))
    auth_token = db.Column(db.String(256))

    def __init__(self, username, password):
        self.username = username
        self.password = hash_password(password)
        self.auth_token = pwd_context.encrypt('{0}{1}'.format(username, app.config['SECRET_KEY']))

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)

    def change_password(self, password):
        self.password = hash_password(password)
        self.auth_token = pwd_context.encrypt('{0}{1}'.format(self.username, app.config['SECRET_KEY']))

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_admin(self):
        if self.username == 'admin':
            return True
        else:
            return False

    def get_id(self):
        try:
            return unicode(self.id)
        except NameError:
            return str(self.id)

    def __repr__(self):
        return '<User %r>' % self.username

    def get_auth_token(self):
        return self.auth_token
