import re
from unidecode import unidecode
from resolver.database import db

SLUG_MAX = 64
TITLE_MAX = 512

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def slugify(text, delim=u'-', lower=True):
    """Generates an ASCII-only slug.
       Written by Armin Ronacher."""
    result = []
    for word in _punct_re.split(text.lower() if lower else text):
        result.extend(unidecode(word).split())
    return unicode(delim.join(result))

# TODO: make types a property of PersistentObject?
object_types = ('work', 'agent', 'concept', 'event')

class PersistentObject(db.Model):
    __tablename__ = 'persistentobject'
    id = db.Column(db.String(64), primary_key=True)
    type = db.Column(db.Enum(*object_types))
    _title =  db.Column('title', db.String(TITLE_MAX))
    slug = db.Column(db.String(SLUG_MAX))

    documents = db.relationship("Document", backref="persistentobject")

    def __init__(self, id, type='work', title=None):
        # Slugify the ID to make sure it causes no problems in URLs
        self.id = slugify(id, lower=False, delim=u'')
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

    title = db.synonym('_title', descriptor=title)
