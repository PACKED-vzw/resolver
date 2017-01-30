from resolver.modules.api.entity import EntityApi, ItemAlreadyExists, ItemDoesNotExist, UnrecognizedEntityType,\
    UnrecognizedDataType, UnrecognizedDocumentType, EntityCollisionException
from resolver.model import Entity, Document, Representation, Data
from resolver.modules.api.tests import *


class EntityTest(ApiTest):

    def test_create_from_rows(self):
        #('PID', 'entity_type', 'title', 'document_type', 'url', 'enabled', 'notes', 'format', 'reference', 'order')
        row_pack = [
            [u'1812-A', u'work', u'Naderend onweer', u'data', u'http://www.vlaamsekunstcollectie.be/collection.aspx?p=0848cab7-2776-4648-9003-25957707491a&inv=1812-A', u'1', u'', u'html', u'', u''],
            [u'1812-A', u'work', u'Naderend onweer', u'representation', u'http://www.vlaamsekunstcollectie.be/proxy.aspx?server=62.221.199.163&port=28301&overlaytext=&overlaytextalpha=14&overlaytextfontname=verdana&overlaytextfontsize=8&overlaytextfontcolor=000000&overlaytextbackgroundcolor=cccccc&cache=yes&borderwidth=0&borderheight=0&bordercolor=999999&passepartoutwidth=6&passepartoutheight=6&passepartoutcolor=ffffff&bg=ffffff&filename=gent%2F1812-A.jpg', u'1', u'', u'1', u'1', u'']
        ]
        import_id = '123'
        entity, documents = EntityApi().create_from_rows(row_pack, import_id)
        d_e = EntityApi().read_by_original_id(row_pack[0][0])
        assert d_e == entity
        assert len(Entity.query.all()) == 1
        d_d = Document.query.filter(Document.entity_id == entity.id).all()
        assert len(d_d) == 2
        assert 'data' in [d.type for d in d_d]
        assert 'representation' in [d.type for d in d_d]
        for d in d_d:
            if d.type == 'data':
                assert d.url == 'http://www.vlaamsekunstcollectie.be/collection.aspx?p=0848cab7-2776-4648-9003-25957707491a&inv=1812-A'
            if d.type == 'representation':
                assert d.url == 'http://www.vlaamsekunstcollectie.be/proxy.aspx?server=62.221.199.163&port=28301&overlaytext=&overlaytextalpha=14&overlaytextfontname=verdana&overlaytextfontsize=8&overlaytextfontcolor=000000&overlaytextbackgroundcolor=cccccc&cache=yes&borderwidth=0&borderheight=0&bordercolor=999999&passepartoutwidth=6&passepartoutheight=6&passepartoutcolor=ffffff&bg=ffffff&filename=gent%2F1812-A.jpg'
            assert d.entity_id == '1812-A'
        assert len(Data.query.all()) == 1
        assert len(Representation.query.all()) == 1

    def test_unrecognizedentitytype_create_from_rows(self):
        # ('PID', 'entity_type', 'title', 'document_type', 'url', 'enabled', 'notes', 'format', 'reference', 'order')
        import_id = '123'
        row_pack = [
            [u'1812-A', u'exception', u'Naderend onweer', u'data',
             u'http://www.vlaamsekunstcollectie.be/collection.aspx?p=0848cab7-2776-4648-9003-25957707491a&inv=1812-A',
             u'1', u'', u'html', u'', u'']
        ]
        self.assertRaises(UnrecognizedEntityType, EntityApi().create_from_rows, row_pack, import_id)

    def test_unrecognizeddatatype_create_from_rows(self):
        import_id = '123'
        row_pack = [
            [u'1813-A', u'work', u'Naderend onweer', u'data',
             u'http://www.vlaamsekunstcollectie.be/collection.aspx?p=0848cab7-2776-4648-9003-25957707491a&inv=1812-A',
             u'1', u'', u'ldf', u'', u'']
        ]
        self.assertRaises(UnrecognizedDataType, EntityApi().create_from_rows, row_pack, import_id)

    def test_unrecognizeddocumenttype_create_from_rows(self):
        import_id = '123'
        row_pack = [
            [u'1813-A', u'work', u'Naderend onweer', u'exception',
             u'http://www.vlaamsekunstcollectie.be/collection.aspx?p=0848cab7-2776-4648-9003-25957707491a&inv=1812-A',
             u'1', u'', u'html', u'', u'']
        ]
        self.assertRaises(UnrecognizedDocumentType, EntityApi().create_from_rows, row_pack, import_id)

    def test_entitycollision_create_from_rows(self):
        import_id = '123'
        row_pack = [
            [u'1814(A', u'work', u'Naderend onweer', u'data',
             u'http://www.vlaamsekunstcollectie.be/collection.aspx?p=0848cab7-2776-4648-9003-25957707491a&inv=1812-A',
             u'1', u'', u'html', u'', u'']
        ]
        EntityApi().create_from_rows(row_pack, import_id)
        row_pack = [
            [u'1814_A', u'work', u'Naderende storm', u'data',
             u'http://www.vlaamsekunstcollectie.be/collection.aspx?p=0848cab7-2776-4648-9003-25957707491a&inv=1812-A',
             u'1', u'', u'html', u'', u'']
        ]
        self.assertRaises(EntityCollisionException, EntityApi().create_from_rows, row_pack, import_id)

    def test_create(self):
        input_data = {
            'PID': u'1812-A',
            'entity_type': u'work',
            'title': u'Naderend onweer',
            }
        min_data = {
            'PID': u'1812-A',
            'entity_type': u'work'
            }
        self.t_create(input_data, min_data, Entity, EntityApi)

    def test_read(self):
        e = EntityApi().create({
            'PID': u'1812-A',
            'entity_type': u'work',
            'title': u'Naderend onweer',
        })
        d_e = EntityApi().read(e.id)
        assert d_e == e

    def test_update(self):
        self.assertRaises(NotImplementedError, EntityApi().update, 1, {})
        return
        input_data = {
            'PID': u'1812-A',
            'entity_type': u'work',
            'title': u'Naderend onweer'
        }
        updated_data = {
            'PID': u'1812-A',
            'entity_type': u'work',
            'title': u'Na regen komt zonneschijn'
        }
        self.t_update(EntityApi, input_data, updated_data)

    def test_delete(self):
        self.assertRaises(NotImplementedError, EntityApi().delete, 1)
        return
        input_data = {
            'PID': u'1812-A',
            'entity_type': u'work',
            'title': u'Naderend onweer',
        }
        self.t_delete(EntityApi, input_data)

    def test_list(self):
        self.assertRaises(NotImplementedError, EntityApi().list)
        return
        input_data = {
            'PID': u'1812-A',
            'entity_type': u'work',
            'title': u'Naderend onweer',
        }
        self.t_list(EntityApi, input_data)
