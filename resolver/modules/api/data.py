from resolver.modules.api.generic import GenericApi, ItemDoesNotExist, ItemAlreadyExists
from resolver.model.data import Data
from resolver.model.document import Document
from resolver.database import db
from sqlalchemy import and_


class DataApi(GenericApi):

    possible_params = ('entity_prim_key', 'format', 'url', 'enabled', 'notes')
    required_params = ('entity_prim_key', 'format')

    def create(self, object_data):
        cleaned_data = self.clean_input_data(Data, object_data, self.possible_params, self.required_params, [])
        try:
            new_document = self.by_format_and_entity_id(cleaned_data['format'], cleaned_data['entity_prim_key'])
        except ItemDoesNotExist:
            new_document = Data(cleaned_data['entity_prim_key'], cleaned_data['format'], url=cleaned_data['url'],
                                enabled=cleaned_data['enabled'], notes=cleaned_data['notes'])
            db.session.add(new_document)
        else:
            new_document.url = cleaned_data['url']
            new_document.enabled = cleaned_data['enabled']
            new_document.notes = cleaned_data['notes']
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

    def by_format_and_entity_id(self, d_format, entity_prim_key):
        existing_document = Data.query.filter(and_(Data.format == d_format, Document.entity_id == entity_prim_key))\
            .first()
        if not existing_document:
            raise ItemDoesNotExist((d_format, entity_prim_key))
        return existing_document
