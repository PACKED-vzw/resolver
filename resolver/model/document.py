from sqlalchemy import Column, Integer, String, Enum, Boolean, ForeignKey
from sqlalchemy.orm import backref, relationship
from resolver.database import Base

document_types = ('data', 'representation')

class Document(Base):
    __tablename__ = 'document'
    id = Column(Integer, primary_key=True)
    type = Column(Enum(*document_types))
    object_id = Column(Integer, ForeignKey("persistentobject.id"))
    url = Column(String(512))
    enabled = Column(Boolean)

    persistent_object = relationship("PersistentObject", backref=backref(''))

    def __init__(self, object_id, type='data', url=None):
        self.object_id = object_id
        self.type = type
        self.url = url
        self.enabled = True

    def __str__(self):
        return '<Document %r>' % (self.id)

    def __repr__(self):
        return '<PObject %r>' % (self.id)
