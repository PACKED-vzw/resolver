from resolver.modules.api.generic import GenericApi, ItemAlreadyExists, ItemDoesNotExist
from resolver.modules.api.data import DataApi
from resolver.modules.api.representation import RepresentationApi
from resolver.model.entity import Entity, EntityCollisionException, EntityPIDExistsException
from resolver.model import document_types, data_formats, entity_types
from resolver.util import cleanID, import_log
from resolver.database import db


class UnrecognizedDocumentType(Exception):
    pass


class UnrecognizedEntityType(Exception):
    pass


class UnrecognizedDataType(Exception):
    pass


class EntityApi(GenericApi):

    keys = ('PID', 'entity_type', 'title', 'document_type', 'url', 'enabled', 'notes', 'format', 'reference', 'order')
    possible_params = ('PID', 'entity_type', 'title')
    required_params = ('PID', 'entity_type')
    simple_params = keys

    def create_from_rows(self, row_pack, import_id):
        rows = []
        for unclean_row in row_pack:
            rows.append(self.prepare_data(unclean_row))
        # Create entity
        if rows[0]['entity_type'] not in entity_types:
            raise UnrecognizedEntityType(rows[0]['entity_type'])
        # All PID, entity_type and title fields in the row_pack are the same
        entity_data = {
            'PID': rows[0]['PID'],
            'entity_type': rows[0]['entity_type'],
            'title': rows[0]['title']
        }
        entity = self.create(entity_data)
        import_log(import_id, 'Added entity {0}'.format(entity))
        documents = []
        for row in rows:
            # Add documents
            if row['document_type'] == 'data':
                if row['format'] == '' or row['format'] not in data_formats:
                    raise UnrecognizedDataType(row['format'])
                document_data = {
                    'entity_id': entity.id,
                    'url': row['url'],
                    'format': row['format'],
                    'enabled': row['enabled'],
                    'notes': row['notes'],
                    'document_type': row['document_type']
                }
                document = DataApi().create(document_data)
                import_log(import_id, 'Added document {0}'.format(document))
                documents.append(document)

            # Add representations
            elif row['document_type'] == 'representation':
                representation_data = {
                    'entity_id': entity.id,
                    'order': row['order'],
                    'label': '',
                    'url': row['url'],
                    'enabled': row['enabled'],
                    'notes': row['notes'],
                    'reference': row['reference'],
                    'document_type': row['document_type']
                }
                document = RepresentationApi().create(representation_data)
                import_log(import_id, 'Added representation {0}'.format(document))
                documents.append(document)

            else:
                raise UnrecognizedDocumentType(row['document_type'])

        # Set the reference representation and the order if it isn't quite right
        representations = RepresentationApi().get_in_order(entity.id)
        has_reference = False
        order = 1
        for representation in representations:
            representation.order = order
            order += 1
            has_reference = representation.reference

        if not has_reference and order > 1:
            representations[0].reference = True
        db.session.commit()
        return entity, documents

    def create(self, input_data):
        cleaned_data = self.clean_input_data(Entity, input_data, self.possible_params, self.required_params, [])
        cleaned_data['cleanPID'] = cleanID(cleaned_data['PID'])
        try:
            new_entity = self.read(cleaned_data['cleanPID'])
        except ItemDoesNotExist:
            new_entity = Entity(cleaned_data['cleanPID'])
            db.session.add(new_entity)
        else:
            if new_entity.original_id != cleaned_data['PID']:
                raise EntityCollisionException(cleaned_data['PID'])

        new_entity.title = cleaned_data['title']
        new_entity.type = cleaned_data['entity_type']
        db.session.flush()
        return new_entity

    def read(self, object_id):
        existing_entity = Entity.query.filter(Entity.id == object_id).first()
        if not existing_entity:
            raise ItemDoesNotExist(Entity.id)
        return existing_entity

    def read_by_original_id(self, original_id):
        existing_entity = entity = Entity.query.filter(Entity.original_id == original_id).first()
        if not existing_entity:
            raise ItemDoesNotExist(original_id)
        return existing_entity

    def prepare_data(self, csv_row):
        a_data = map(lambda x: '' if x is None else x, csv_row)
        t_data = zip(self.keys, a_data)
        d_data = dict(t_data)
        return d_data

    def update(self, object_id, object_data):
        raise NotImplementedError()

    def delete(self, object_id):
        raise NotImplementedError()

    def list(self):
        raise NotImplementedError()

    def rollback(self):
        db.session.rollback()
