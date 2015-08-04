import re, requests
from urlparse import urlparse, urlunparse
from resolver import app
from resolver.database import db
from resolver.util import log
import resolver.kvstore as kvstore

document_types = ('data', 'representation')

class Document(db.Model):
    __tablename__ = 'document'
    id = db.Column(db.Integer, primary_key=True)
    entity_id = db.Column(db.String(64), db.ForeignKey("entity.id",
                                                       onupdate='cascade',
                                                       ondelete='cascade'))
    _enabled = db.Column('enabled', db.Boolean)
    notes = db.Column(db.Text)
    _url = db.Column('url', db.String(512))
    type = db.Column(db.String(50))
    hits = db.relationship('DocumentHit',
                           #cascade='all,delete',
                           cascade='all, delete-orphan',
                           backref='document')

    __mapper_args__ = {
        'polymorphic_identity':'document',
        'polymorphic_on':type
    }

    def __init__(self, entity_id, url=None, enabled=True, notes=None):
        self.url = url
        self.entity_id = entity_id
        self.enabled = enabled
        self.notes = notes

    def __repr__(self):
        raise Exception("Implement me")

    def to_dict(self):
        return {'url':self.url if self.url else "",
                'enabled':self.enabled,
                'id':self.id,
                'type':self.type,
                'notes':self.notes,
                'resolves':self.resolves,
                'entity':self.entity_id}

    @property
    def persistent_uri(self):
        raise Exception("Implement me")

    @property
    def resolves(self):
        if self.url:
            try:
                r = requests.head(self.url, allow_redirects=True)
                if r.status_code == 200:
                    return True
                else:
                    return False
            except:
                return False
        else:
            return False

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        # TODO: URL validation here

        old = self._url
        if url:
            u = urlparse(url)
            if u.scheme:
                self._url = url
            else:
                self._url = urlunparse(('http',)+u[1:])
        else:
            self._url = None

        if old != self._url:
            log(self.entity_id, "Changed URL from '%s' to '%s' for %s" %
                (old, self._url, self))

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        value = bool(value)
        if self._enabled and (not value):
            log(self.entity_id, "Disabled document %s" % self)
        elif (not self._enabled) and value:
            log(self.entity_id, "Enabled document %s" % self)

        self._enabled = value

    enabled = db.synonym('_enabled', descriptor=enabled)
    url = db.synonym('_url', descriptor=url)
