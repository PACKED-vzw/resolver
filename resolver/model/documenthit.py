from datetime import datetime
from urlparse import urlparse
from resolver.database import db

def clean_url(url):
    """Cleans up an url so only the (sub)domain remains.
       Ex.: http://some.weird.doma.in/search?q=foo/bar
            => some.weird.doma.in """
    return urlparse(url).netloc

class DocumentHit(db.Model):
    __tablename__ = 'documenthit'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(15))
    document_id = db.Column(db.Integer, db.ForeignKey("document.id",
                                                      onupdate="cascade",
                                                      ondelete="cascade"))
    referrer = db.Column(db.String(128))
    timestamp = db.Column(db.DateTime)

    document = db.relationship("Document")

    def __init__(self, document, ip, referrer):
        self.document_id = document
        self.ip = ip
        self.referrer = clean_url(referrer) if referrer else referrer
        self.timestamp = datetime.now()

    def __repr__(self):
        return '<DocumentHit, time=%s, document=%s, type=%s>' %\
            (self.timestamp, self.document_id, self.document.type)
