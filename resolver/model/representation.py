from resolver import app
from resolver.database import db
from resolver.model import Document
import resolver.kvstore as kvstore

LABEL_MAX = 64

class Representation(Document):
    __tablename__ = 'representation'
    id = db.Column(db.Integer, db.ForeignKey('document.id'), primary_key=True)
    order = db.Column(db.Integer)
    reference = db.Column(db.Boolean)
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
        if label:
            return '<Representation(%s), entity=%s, label=%s, url=%s, order=%s, ref=%s>' %\
                (self.id, self.entity_id, self.label, self.url, self.order,
                 self.reference)
        else:
            return '<Representation(%s), entity=%s, url=%s, order=%s, ref=%s>' %\
                (self.id, self.entity_id, self.url, self.order, self.reference)

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
        dict['label'] = self.label
        return dict
