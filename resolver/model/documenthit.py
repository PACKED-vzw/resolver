from sqlalchemy import Column, Integer, String, Enum, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import backref, relationship
from datetime import datetime
from urlparse import urlparse
from resolver.database import Base

def clean_url(url):
    """Cleans up an url so only the (sub)domain remains.
       Ex.: http://some.weird.doma.in/search?q=foo/bar
            => some.weird.doma.in """
    return urlparse(url).netloc

class DocumentHit(Base):
    __tablename__ = 'documenthit'
    id = Column(Integer, primary_key=True)
    ip = Column(String(15))
    document_id = Column(Integer, ForeignKey("document.id",
                                             onupdate="cascade",
                                             ondelete="cascade"))
    referrer = Column(String(128))
    timestamp = Column(DateTime)

    document = relationship("Document")

    def __init__(self, document, ip, referrer):
        self.document_id = document
        self.ip = ip
        self.referrer = clean_url(referrer) if referrer else referrer
        self.timestamp = datetime.now()

    def __repr__(self):
        return '<DocumentHit, time=%s, document=%s, type=%s>' %\
            (self.timestamp, self.document_id, self.document.type)
