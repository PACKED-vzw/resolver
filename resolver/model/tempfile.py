from datetime import datetime
from resolver.database import db


class TempFile(db.Model):
    __tablename__ = 'tempfile'
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime)
    path = db.Column(db.Text)

    def __init__(self, path):
        self.path = path
        self.created = datetime.now()