from resolver.modules.api.representation import RepresentationApi, ItemDoesNotExist, ItemAlreadyExists
from resolver.modules.api.entity import EntityApi
from resolver.model import Entity, Document, Representation, Data
from resolver.modules.api.tests import *


class RepresentationTest(ApiTest):

    def test_create(self):
        entity = EntityApi().create({'PID': u'1812-A', 'entity_type': u'work'})
        input_data = {
            'entity_prim_key': entity.prim_key,
            'order': 1,
            'label': 'Foo',
            'url': 'http://www.foo.bar',
            'enabled': 1,
            'notes': 'A Test',
            'reference': 1,
            'document_type': 'representation'
        }
        input_data_min = {
            'entity_prim_key': entity.prim_key,
            'order': 1
        }
        self.t_create(input_data, input_data_min, Representation, RepresentationApi)

    def test_by_entity_prim_key_url_and_type(self):
        entity = EntityApi().create({'PID': u'1812-A', 'entity_type': u'work'})
        input_data = {
            'entity_prim_key': entity.prim_key,
            'order': 1,
            'label': 'Foo',
            'url': 'http://www.foo.bar',
            'enabled': 1,
            'notes': 'A Test',
            'reference': 1,
            'document_type': 'representation'
        }
        r = RepresentationApi().create(input_data)
        l = RepresentationApi().by_entity_prim_key_url_and_type(entity.prim_key, 'http://www.foo.bar', 'representation')
        assert r == l

    def test_get_in_order(self):
        entity = EntityApi().create({'PID': u'1812-A', 'entity_type': u'work'})
        input_data = {
            'entity_prim_key': entity.prim_key,
            'order': 1,
            'label': 'Foo',
            'url': 'http://www.foo.bar',
            'enabled': 1,
            'notes': 'A Test',
            'reference': 1,
            'document_type': 'representation'
        }
        r_a = RepresentationApi().create(input_data)
        input_data_extra = {
            'entity_prim_key': entity.prim_key,
            'order': 2,
            'label': 'Foo',
            'url': 'http://www.foo.bar.x',
            'enabled': 1,
            'notes': 'A Test (2)',
            'reference': 0,
            'document_type': 'representation'
        }
        r_b = RepresentationApi().create(input_data_extra)
        l = RepresentationApi().get_in_order(entity.prim_key)
        assert len(l) == 2
        assert l[0] == r_a
        assert l[1] == r_b

    def test_read(self):
        self.assertRaises(NotImplementedError, RepresentationApi().read, 1)
        return
        entity = EntityApi().create({'PID': u'1812-A', 'entity_type': u'work'})
        input_data_min = {
            'entity_prim_key': entity.prim_key,
            'order': 1
        }
        self.t_read(RepresentationApi, input_data_min)

    def test_update(self):
        self.assertRaises(NotImplementedError, RepresentationApi().update, 1, {})
        return
        entity = EntityApi().create({'PID': u'1812-A', 'entity_type': u'work'})
        input_data = {
            'entity_prim_key': entity.prim_key,
            'order': 1,
            'label': 'Foo',
            'url': 'http://www.foo.bar',
            'enabled': 1,
            'notes': 'A Test',
            'reference': 1,
            'document_type': 'representation'
        }
        updated_data = {
            'entity_prim_key': entity.prim_key,
            'order': 1,
            'label': 'Foobar',
            'url': 'http://www.foo.bar.x',
            'enabled': 1,
            'notes': 'A Test (2)',
            'reference': 1,
            'document_type': 'representation'
        }
        self.t_update(RepresentationApi, input_data, updated_data)

    def test_delete(self):
        self.assertRaises(NotImplementedError, RepresentationApi().delete, 1)
        return
        entity = EntityApi().create({'PID': u'1812-A', 'entity_type': u'work'})
        input_data_min = {
            'entity_prim_key': entity.prim_key,
            'order': 1
        }
        self.t_delete(RepresentationApi, input_data_min)

    def test_list(self):
        self.assertRaises(NotImplementedError, RepresentationApi().list)
        return
        entity = EntityApi().create({'PID': u'1812-A', 'entity_type': u'work'})
        input_data_min = {
            'entity_prim_key': entity.prim_key,
            'order': 1
        }
        self.t_list(RepresentationApi, input_data_min)
