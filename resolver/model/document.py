import re
from resolver import app
from resolver.database import db

# TODO: make types a property of Document?
document_types = ('data', 'representation')

class Document(db.Model):
    __tablename__ = 'document'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(*document_types, name='DocumentType'))
    object_id = db.Column(db.String(64), db.ForeignKey("persistentobject.id",
                                                       onupdate="cascade",
                                                       ondelete="cascade"))
    url = db.Column(db.String(512))
    enabled = db.Column(db.Boolean)
    notes = db.Column(db.Text)

    # TODO: is this valid?
    persistent_object = db.relationship("PersistentObject", backref=db.backref(''))

    def __init__(self, object_id, type, url=None, enabled=True, notes=None):
        self.object_id = object_id
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
                      [('%id', self.object_id),
                       ('%otype', self.persistent_object.type),
                       ('%dtype', self.type),
                       ('%slug', self.persistent_object.slug)],
                      '/'+app.config['FULL_URL'])
