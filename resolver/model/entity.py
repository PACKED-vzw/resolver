import re
from unidecode import unidecode
from resolver import app
from resolver.database import db
import resolver.kvstore as kvstore

SLUG_MAX = 64
TITLE_MAX = 512
SLUG_DEFAULT = "untitled"

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
_clean_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|}]+')

def slugify(text):
    """Generates an ASCII-only slug.
       Written by Armin Ronacher."""
    result = []
    for word in _punct_re.split(text.lower()):
        result.extend(unidecode(word).split())
    return unicode('-'.join(result))

def cleanID(ID):
    """Adapted from slugify, but allows [,.]"""
    result = []
    for word in _clean_re.split(ID):
        result.extend(unidecode(word).split())
    return unicode(''.join(result))

# TODO: make types a property of Entity?
entity_types = ('work', 'agent', 'concept', 'event')

class Entity(db.Model):
    __tablename__ = 'entity'
    # TODO: make maximum ID length a global var?
    # it's also used in other classes, so it might not be a bad idea
    _id = db.Column('id', db.String(64), primary_key=True)
    type = db.Column(db.Enum(*entity_types, name='EntityType'))
    _title =  db.Column('title', db.String(TITLE_MAX))
    slug = db.Column(db.String(SLUG_MAX))

    _documents = db.relationship("Document",
                                 cascade='all,delete',
                                 backref='entity',
                                 order_by='Document.type')

    def __init__(self, id, type='work', title=None):
        self.id = id
        self.type = type
        self.title = title

    def __repr__(self):
        return '<Entity(%s), id=%s, title=%s>' %\
            (self.type, self.id, self.title)

    @property
    def persistent_uri(self):
        url = app.config['BASE_URL']+'/collection/%s' % self.id

        if kvstore.get('titles_enabled'):
            return [url, url+'/%s'%self.slug]
        else:
            return [url]

    @property
    def persistent_uris(self):
        uris = self.persistent_uri
        for doc in self.documents:
            uris += doc.persistent_uri

        return uris

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.slug = slugify(value)[:64] if value else SLUG_DEFAULT

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        # TODO: error if id != cleanID(id) ?
        self._id = cleanID(value)

    @property
    def documents(self):
        def sort_help(a, b):
            # Helper function for sorting the documents list
            if (a.type=='data') or (b.type=='data'):
                return 0
            else:
                return -1 if a.order < b.order else 1

        docs = self._documents
        return sorted(docs, sort_help)

    title = db.synonym('_title', descriptor=title)
    id = db.synonym('_id', descriptor=id)
