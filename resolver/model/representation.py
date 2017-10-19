from resolver import app
from resolver.database import db
from resolver.model import Document
from resolver.util import log
import resolver.kvstore as kvstore
import urllib
import urlparse

LABEL_MAX = 64

class Representation(Document):
    __tablename__ = 'representation'
    id = db.Column(db.Integer,
                   db.ForeignKey('document.id',
                                 onupdate='cascade',
                                 ondelete='cascade'),
                   primary_key=True)
    order = db.Column(db.Integer)
    _reference = db.Column('reference', db.Boolean)
    label = db.Column(db.String(LABEL_MAX))

    __mapper_args__ = {
        'polymorphic_identity':'representation'
    }

    def __init__(self, entity, order, label=None, url=None, enabled=True,
                 notes=None, reference=False):
        super(Representation, self).__init__(entity, url=url, enabled=enabled,
                                             notes=notes)
        self.order = order
        self.reference = reference
        self.label = label

    def __repr__(self):
        if self.label:
            return '<Representation(%s), entity=%s, label=%s, url=%s, order=%s, ref=%s, enabled=%s>' %\
                (self.id, self.entity_id, self.label, self.url, self.order,
                 self.reference, self.enabled)
        else:
            return '<Representation(%s), entity=%s, url=%s, order=%s, ref=%s>' %\
                (self.id, self.entity_id, self.url, self.order, self.reference)

    @property
    def persistent_uri(self):
        uri = app.config['BASE_URL']
        uri += '/collection/%s/representation/%s/%s' % (self.entity.type,
                                                        self.entity_id,
                                                        self.order)

        p = urlparse.urlparse(uri, 'http')
        netloc = p.netloc or p.path
        path = p.path if p.netloc else ''
        p = urlparse.ParseResult('http', netloc, path, *p[3:])
        uri = p.geturl()

        uris = [uri]

        if kvstore.get('titles_enabled'):
            uris.append(uri+'/'+self.entity.slug)
        if self.reference:
            uri = app.config['BASE_URL'] + '/collection/%s/representation/%s' % (self.entity.type, self.entity_id)

            p = urlparse.urlparse(uri, 'http')
            netloc = p.netloc or p.path
            path = p.path if p.netloc else ''
            p = urlparse.ParseResult('http', netloc, path, *p[3:])
            uri = p.geturl()

            uris.append(uri)

        return uris

    def to_dict(self):
        dict = super(Representation, self).to_dict()
        dict['order'] = self.order
        dict['reference'] = self.reference
        dict['label'] = self.label
        return dict

    @property
    def reference(self):
        return self._reference

    @reference.setter
    def reference(self, value):
        value = bool(value)
        if self._reference and (not value):
            log(self.entity_id, "Removed as reference: %s" % self)
        elif (not self._reference) and value:
            log(self.entity_id, "Set as reference: %s" % self)

        self._reference = value

    reference = db.synonym('_reference', descriptor=reference)
