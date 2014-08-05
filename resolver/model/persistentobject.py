from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import backref, relationship
from resolver.database import Base

# TODO: make types a property of PersistentObject?
object_types = ('work', 'agent', 'concept', 'event')

class PersistentObject(Base):
    __tablename__ = 'persistentobject'
    id = Column(String(64), primary_key=True)
    type = Column(Enum(*object_types))
    title =  Column(String(512))

    documents = relationship("Document", backref="persistentobject")

    @property
    def documents_by_type(self):
        return {d.type: d for d in self.documents}

    def __init__(self, id=None, type='work', title=None):
        self.id = id
        self.type = type
        self.title = title

    def __str__(self):
        return '<PObject %r>' % (self.id)

    def __repr__(self):
        return '<PObject %r>' % (self.id)
