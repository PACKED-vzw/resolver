import re
from unidecode import unidecode
from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import backref, relationship, synonym
from resolver.database import Base

SLUG_MAX = 64
TITLE_MAX = 512

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def slugify(text, delim=u'-'):
    """Generates an ASCII-only slug.
       Written by Armin Ronacher."""
    result = []
    for word in _punct_re.split(text.lower()):
        result.extend(unidecode(word).split())
    return unicode(delim.join(result))

# TODO: make types a property of PersistentObject?
object_types = ('work', 'agent', 'concept', 'event')

class PersistentObject(Base):
    __tablename__ = 'persistentobject'
    id = Column(String(64), primary_key=True)
    type = Column(Enum(*object_types))
    _title =  Column('title', String(TITLE_MAX))
    slug = Column(String(SLUG_MAX))

    documents = relationship("Document", backref="persistentobject")

    def __init__(self, id, type='work', title=None):
        self.id = id
        self.type = type
        self.title = title
        self.slug = slugify(title)[:64] if title else ""

    def __repr__(self):
        return '<Object(%s), id=%s, title=%s>' %\
            (self.type, self.id, self.title)

    @property
    def documents_by_type(self):
        return {d.type: d for d in self.documents}

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.slug = slugify(value)[:64] if value else ""

    title = synonym('_title', descriptor=title)
