from datetime import datetime
from resolver.database import db

# TODO: put all these globals in a file
ID_MAX = 64

class Log(db.Model):
    __tablename__ = 'log'
    id = db.Column(db.Integer, primary_key=True)
    entity = db.Column(db.String(ID_MAX))
    user = db.Column(db.String(32))
    timestamp = db.Column(db.DateTime)
    data = db.Column(db.Text)

    def __init__(self, entity, user, data):
        self.entity = entity
        self.data = data
        self.user = user
        self.timestamp = datetime.now()

    def __repr__(self):
        return 'Entity `%s\', user `%s\' (%s): %s' %\
            (self.entity, self.user, self.timestamp, self.data)
