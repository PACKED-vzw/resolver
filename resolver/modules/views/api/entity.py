from resolver.modules.api.entity import EntityApi, ItemDoesNotExist
from resolver import app


class EntityViewApi:

    def get(self, entity_id):
        try:
            existing_entity = EntityApi().read_by_pid(entity_id)
        except ItemDoesNotExist:
            return None
        return self.output(existing_entity)

    def get_original(self, original_entity_id):
        try:
            existing_entity = EntityApi().read_by_original_id(original_entity_id)
        except ItemDoesNotExist:
            return None
        return self.output(existing_entity)

    def output(self, entity):
        return {
            'id': entity.id,
            'domain': entity.domain,
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
