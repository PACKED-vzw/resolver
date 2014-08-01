from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import backref, relationship
from resolver.database import Base
from resolver.config import Config
from hashlib import sha256

def hash_password(password):
    m = sha256()
    m.update(Config.SALT + password)
    return m.hexdigest()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32))
    password = Column(String(64))

    def __init__(self, username, password):
        self.username = username
        self.password = hash_password(password)

    def verify_password(self, password):
        return self.password == hash_password(password)

    def change_password(self, password):
        self.password = hash_password(password)
