from resolver.modules.api.generic import GenericApi, ItemDoesNotExist, ItemAlreadyExists
from resolver.model.representation import Representation
from resolver.model.document import Document
from resolver.database import db
from sqlalchemy import and_


class RepresentationApi(GenericApi):
    possible_params = ('entity_prim_key', 'order', 'label', 'url', 'enabled', 'notes', 'reference', 'document_type')
    required_params = ('entity_prim_key', 'order')

    def create(self, object_data):
        cleaned_data = self.clean_input_data(Representation, object_data, self.possible_params, self.required_params,
                                             [])
        if cleaned_data['url'] == '':
            cleaned_data['url'] = None
        try:
            new_document = self.by_entity_prim_key_url_and_type(cleaned_data['entity_prim_key'], cleaned_data['url'],
                                                                cleaned_data['document_type'])
        except ItemDoesNotExist:
            if cleaned_data['order'] and cleaned_data['order'] != '' and cleaned_data['order'] != 0:
                i_order = int(cleaned_data['order'])
            else:
                # The order is amount_of_representations + 1
                i_order = Representation.query.filter(Document.entity_id == cleaned_data['entity_prim_key']).count() + 1
            new_document = Representation(cleaned_data['entity_prim_key'], i_order, enabled=cleaned_data['enabled'],
                                          url=cleaned_data['url'], notes=cleaned_data['notes'])
            db.session.add(new_document)
        else:
            new_document.url = cleaned_data['url']
            new_document.enabled = cleaned_data['enabled']
            new_document.notes = cleaned_data['notes']

        # Set the "reference" representation
        if cleaned_data['reference'] == 1:
            db_ref = Representation.query.filter(and_(Document.entity_id == cleaned_data['entity_prim_key'],
                                                      Representation.reference is True)).first()
            if db_ref:
                db_ref.reference = False
            new_document.reference = True

        db.session.flush()
        return new_document

    def read(self, object_id):
        raise NotImplementedError()

    def update(self, object_id, object_data):
        raise NotImplementedError()

    def delete(self, object_id):
        raise NotImplementedError()

    def list(self):
        raise NotImplementedError()

    def by_entity_prim_key_url_and_type(self, entity_prim_key, url, document_type):
        existing_document = Representation.query.filter(and_(Document.entity_id == entity_prim_key,
                                                             Document.url == url,
                                                             Document.type == document_type)).first()
        if not existing_document:
            raise ItemDoesNotExist((entity_prim_key, url, document_type))
        return existing_document

    def get_in_order(self, entity_prim_key):
        return Representation.query.filter(Document.entity_id == entity_prim_key).order_by(
            Representation.order.asc()).all()
