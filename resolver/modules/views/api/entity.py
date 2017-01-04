from resolver.model.entity import Entity
from resolver import app


class EntityApi:

    def get(self, entity_id):
        entity = Entity.query.filter(Entity.id == entity_id).first()
        if entity:
            return self.output(entity)
        else:
            return None

    def get_original(self, original_entity_id):
        entity = Entity.query.filter(Entity.original_id == original_entity_id).first()
        if entity:
            return self.output(entity)
        else:
            return None

    def output(self, entity):
        return {
            'id': entity.id,
            'domain': app.config['BASE_URL'],
            'type': entity.type,
            'work_pid': entity.work_pid,
            'persistentURIs': entity.persistent_uris,
            'documents': [d.id for d in entity.documents],
            'data_pids': self.get_data_pids(entity)
        }

    def get_data_pids(self, entity):
        data_pids = []
        for document in entity.documents:
            if document.type == 'data':
                data_pids.append(document.data_pid)
        return data_pids
