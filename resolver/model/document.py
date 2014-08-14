import re
from resolver import app
from resolver.database import db

# TODO: make types a property of Document?
document_types = ('data', 'representation')

class Document(db.Model):
    __tablename__ = 'document'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(*document_types, name='DocumentType'))
    entity_id = db.Column(db.String(64), db.ForeignKey("entity.id",
                                                       onupdate="cascade",
                                                       ondelete="cascade"))
    url = db.Column(db.String(512))
    enabled = db.Column(db.Boolean)
    notes = db.Column(db.Text)

    entity = db.relationship("Entity", backref=db.backref(''))

    def __init__(self, entity_id, type, url=None, enabled=True, notes=None):
        self.entity_id = entity_id
        self.type = type
        self.url = url
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
