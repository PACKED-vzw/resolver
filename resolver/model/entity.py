import re
from unidecode import unidecode
from resolver import app
from resolver.database import db
from resolver.exception import EntityPIDExistsException,\
    EntityCollisionException
from resolver.util import cleanID, log
import resolver.kvstore as kvstore
import urllib
import urlparse

ID_MAX = 64
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

# TODO: make types a property of Entity?
entity_types = ('work', 'agent', 'concept', 'event')


class Entity(db.Model):
    __tablename__ = 'entity'
    _id = db.Column('id', db.String(ID_MAX), primary_key=True)
    original_id = db.Column(db.String(ID_MAX))
    _type = db.Column('type', db.Enum(*entity_types, name='EntityType'))
    _title =  db.Column('title', db.String(TITLE_MAX))
    slug = db.Column(db.String(SLUG_MAX))

    _documents = db.relationship("Document",
                                 #cascade='all,delete',
                                 cascade='all,delete-orphan',
                                 backref='entity',
                                 order_by='Document.type')

    def __init__(self, id, type='work', title=None):
        self.id = id
        self.type = type
        self.title = title

    def __repr__(self):
        return '<Entity(%s), id=%s (%s), title=%s>' %\
            (self.type, self.id, self.original_id, self.title)

    @property
    def persistent_uri(self):
        url = app.config['BASE_URL']+'/collection/%s' % self.id

        p = urlparse.urlparse(url, 'http')
        netloc = p.netloc or p.path
        path = p.path if p.netloc else ''
        p = urlparse.ParseResult('http', netloc, path, *p[3:])
        url = p.geturl()

        if kvstore.get('titles_enabled'):
            return [url, url+'/%s'%self.slug]
        else:
            return [url]

    @property
    def work_pid(self):
        url = '{base_url}/collection/{entity_id}'.format(
            base_url=app.config['BASE_URL'],
            entity_id=self.id
        )
        return url

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
        if self._title != value:
            log(self.id, "Changed title from '%s' to '%s'" %
                (self._title, value))

        self._title = value
        self.slug = slugify(value)[:64] if value else SLUG_DEFAULT

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        new_id = cleanID(value)
        ent = Entity.query.filter(Entity.id == new_id).first()
        # check against self (in case we're changing an existing entity's PID)
        if ent and not ent == self:
            # PID already in DB. If the unclean PID is not equal to the existing
            # entity's original PID, this is probably a collision.
            if value == ent.original_id:
                raise EntityPIDExistsException()
            else:
                raise EntityCollisionException(ent.original_id)

        if self._id != new_id:
            log(self.id, "Changed id from '%s' to '%s'" % (self._id, new_id))

        self.original_id = value
        self._id = new_id

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        if value not in entity_types:
            raise Exception("Wrong entity type")

        if self._type != value:
            log(self.id, "Changed type from '%s' to '%s'" % (self._type, value))

        self._type = value

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

    @property
    def active_documents(self):
        count = 0
        for document in self.documents:
            if document.enabled and\
               (document.url != '' or document.url != None):
                count += 1

        return count

    id = db.synonym('_id', descriptor=id)
    title = db.synonym('_title', descriptor=title)
    type = db.synonym('_type', descriptor=type)
