from resolver.modules.api.data import DataApi, ItemDoesNotExist, ItemAlreadyExists
from resolver.modules.api.entity import EntityApi
from resolver.model import Document, Data
from resolver.modules.api.tests import *


class DataTest(ApiTest):

    def test_create(self):
        #'entity_prim_key', 'format', 'url', 'enabled', 'notes'
        entity = EntityApi().create({'PID': '123', 'entity_type': 'work'})
        input_data_max = {
            'entity_prim_key': entity.prim_key,
            'format': 'html',
            'url': 'http://foo.bar',
            'enabled': 1,
            'notes': 'A Test'
        }
        input_data_min = {
            'entity_prim_key': entity.prim_key,
            'format': 'html'
        }
        d = self.t_create(api_class=DataApi, db_class=Data, input_data_max=input_data_max, input_data_min=input_data_min)
        assert d.entity_prim_key == entity.prim_key

    def test_by_format_and_identity_prim_key(self):
        entity = EntityApi().create({'PID': '123', 'entity_type': 'work'})
        d = DataApi().create(
            {'entity_prim_key': entity.prim_key, 'format': 'html', 'url': 'http://foo.bar', 'enabled': 1, 'notes': 'A Test'})
        d_e = DataApi().by_format_and_entity_id('html', entity.prim_key)
        assert d == d_e

    def test_read(self):
        self.assertRaises(NotImplementedError, DataApi().read, '1')
        return
        entity = EntityApi().create({'PID': '123', 'entity_type': 'work'})
        self.t_read(api_class=DataApi, input_data={'entity_prim_key': entity.prim_key, 'format': 'html'})

    def test_update(self):
        self.assertRaises(NotImplementedError, DataApi().update, 1, {})
        return
        entity = EntityApi().create({'PID': '123', 'entity_type': 'work'})
        input_data = {'entity_prim_key': entity.prim_key, 'format': 'html', 'url': 'http://foo.bar', 'enabled': 1, 'notes': 'A Test'}
        updated_data = {'entity_prim_key': entity.prim_key, 'format': 'pdf', 'url': 'http://foo.bar', 'enabled': 1, 'notes': 'A Test'}
        self.t_update(api_class=DataApi, input_data=input_data, updated_data=updated_data)

    def test_delete(self):
        self.assertRaises(NotImplementedError, DataApi().delete, 1)
        return
        entity = EntityApi().create({'PID': '123', 'entity_type': 'work'})
        self.t_delete(api_class=DataApi, input_data={'entity_prim_key': entity.prim_key, 'format': 'html'})

    def test_list(self):
        self.assertRaises(NotImplementedError, DataApi().list)
        return
        entity = EntityApi().create({'PID': '123', 'entity_type': 'work'})
        self.t_list(api_class=DataApi, input_data={'entity_prim_key': entity.prim_key, 'format': 'html'})
