from resolver.database import db

class KVPair(db.Model):
    __tablename__ = 'kvpair'
    key = db.Column(db.String(64), primary_key=True)
    value = db.Column(db.Text)

    def __init__(self, key, value):
        self.key = key
        self.value = value
