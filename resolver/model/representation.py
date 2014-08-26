from resolver import app
from resolver.database import db
from resolver.model import Document
import resolver.kvstore as kvstore

class Representation(Document):
    __tablename__ = 'representation'
    id = db.Column(db.Integer, db.ForeignKey('document.id'), primary_key=True)
    order = db.Column(db.Integer)
    reference = db.Column(db.Boolean)

    __mapper_args__ = {
        'polymorphic_identity':'representation'
    }

    def __init__(self, entity, order, url=None, enabled=True, notes=None,
                 reference=False):
        super(Representation, self).__init__(entity, url=url, enabled=enabled,
                                             notes=notes)
        self.order = order
        self.reference = reference

    def __repr__(self):
        return '<Representation(%s), entity=%s, url=%s>' %\
            (self.id, self.entity_id, self.url)

    @property
    def persistent_uri(self):
        uri = app.config['BASE_URL']
        uri += '/collection/%s/representation/%s/%s' % (self.entity.type,
                                                        self.entity_id,
                                                        self.order)

        if kvstore.get('titles_enabled'):
            return [uri, uri+'/'+self.entity.slug]
        else:
            return [uri]

    def to_dict(self):
        dict = super(Representation, self).to_dict()
        dict['order'] = self.order
        dict['reference'] = self.reference
        return dict
