from datetime import datetime
from resolver.database import db

# TODO: put all these globals in a file
ID_MAX = 64


class ImportLog(db.Model):
    __tablename__ = 'ImportLog'
    id = db.Column(db.Integer, primary_key=True)
    import_id = db.Column(db.String(ID_MAX))
    # XXX: Do not add a foreign key constraint referencing User
    user = db.Column(db.String(32))
    timestamp = db.Column(db.DateTime)
    data = db.Column(db.Text)

    def __init__(self, import_id, user, data):
        self.import_id = import_id
        self.data = data
        self.user = user
        self.timestamp = datetime.now()

    def __repr__(self):
        return 'Import `%s\', user `%s\' (%s): %s' %\
            (self.import_id, self.user, self.timestamp, self.data)
