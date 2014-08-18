import re, requests
from urlparse import urlparse, urlunparse
from resolver import app
from resolver.database import db

# TODO: make types a property of Document?
document_types = ('data', 'representation')

class Document(db.Model):
    __tablename__ = 'document'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(*document_types, name='DocumentType'))
    entity_id = db.Column(db.String(64), db.ForeignKey("entity.id"))
    url = db.Column(db.String(512))
    enabled = db.Column(db.Boolean)
    notes = db.Column(db.Text)
    hits = db.relationship("DocumentHit",
                           cascade='all,delete',
                           backref='document')

    def __init__(self, entity_id, type, url=None, enabled=True, notes=None):
        if url:
            u = urlparse(url)
            if u.scheme:
                self.url = url
            else:
                self.url = urlunparse(('http',)+u[1:])
        else:
            self.url = None

        self.entity_id = entity_id
        self.type = type
        self.enabled = enabled
        self.notes = notes

    def __repr__(self):
        return '<Document(%s), enabled=%s, url=%s>' %\
            (self.type, self.enabled,self.url)

    @property
    def persistent_uri(self):
        return reduce(lambda str, t: re.sub(t[0], t[1], str),
                      [('%id', self.entity_id),
                       ('%etype', self.entity.type),
                       ('%dtype', self.type),
                       ('%slug', self.entity.slug)],
                      '/'+app.config['FULL_URL'])

    @property
    def resolves(self):
        if self.url:
            r = requests.head(self.url, allow_redirects=True)
            if r.status_code == 200:
                return True
            else:
                return False
        else:
            return False
