from sqlalchemy import Column, Integer, String, Enum, Boolean, ForeignKey, Text
from sqlalchemy.orm import backref, relationship
from resolver.database import Base

# TODO: make types a property of Document?
document_types = ('data', 'representation')

class Document(Base):
    __tablename__ = 'document'
    id = Column(Integer, primary_key=True)
    type = Column(Enum(*document_types))
    object_id = Column(String(64), ForeignKey("persistentobject.id",
                                              onupdate="cascade",
                                              ondelete="cascade"))
    url = Column(String(512))
    enabled = Column(Boolean)
    notes = Column(Text)

    # TODO: is this valid?
    persistent_object = relationship("PersistentObject", backref=backref(''))

    def __init__(self, object_id, type, url=None, enabled=True, notes=None):
        self.object_id = object_id
        self.type = type
        self.url = url
        self.enabled = enabled
        self.notes = notes

    def __repr__(self):
        return '<Document(%s), enabled=%s, url=%s>' %\
            (self.type, self.enabled,self.url)
