from resolver.modules.importer.tests import ImporterTest
from resolver.modules.importer.csv import CSVImporter
from resolver.modules.api.entity import EntityApi
from resolver.model import Entity, Data, Document, Representation


class CSVTest(ImporterTest):

    def test_csv_importer(self):
        records = [
            [u'1812-A', u'work', u'Naderend onweer', u'data',
             u'http://www.vlaamsekunstcollectie.be/collection.aspx?p=0848cab7-2776-4648-9003-25957707491a&inv=1812-A',
             u'1', u'', u'html', u'', u''],
            [u'1812-A', u'work', u'Naderend onweer', u'representation',
             u'http://www.vlaamsekunstcollectie.be/proxy.aspx?server=62.221.199.163&port=28301&overlaytext=&overlaytextalpha=14&overlaytextfontname=verdana&overlaytextfontsize=8&overlaytextfontcolor=000000&overlaytextbackgroundcolor=cccccc&cache=yes&borderwidth=0&borderheight=0&bordercolor=999999&passepartoutwidth=6&passepartoutheight=6&passepartoutcolor=ffffff&bg=ffffff&filename=gent%2F1812-A.jpg',
             u'1', u'', u'1', u'1', u''],
            [u'1813-A', u'work', u'Na de regen', u'data',
             u'http://www.vlaamsekunstcollectie.be/collection.aspx?p=0848cab7-2776-4648-9003-25957707491a&inv=1812-A',
             u'1', u'', u'html', u'', u''],
            [u'1813-A', u'work', u'Na de regen', u'representation',
             u'http://www.vlaamsekunstcollectie.be/proxy.aspx?server=62.221.199.163&port=28301&overlaytext=&overlaytextalpha=14&overlaytextfontname=verdana&overlaytextfontsize=8&overlaytextfontcolor=000000&overlaytextbackgroundcolor=cccccc&cache=yes&borderwidth=0&borderheight=0&bordercolor=999999&passepartoutwidth=6&passepartoutheight=6&passepartoutcolor=ffffff&bg=ffffff&filename=gent%2F1812-A.jpg',
             u'1', u'', u'1', u'1', u''],
        ]
        import_id = '123'
        c_importer = CSVImporter(records, import_id)
        c_importer.store()

        # Most tests are done by test_entity
        assert len(Entity.query.all()) == 1
        d_e = EntityApi().read_by_original_id(records[0][0])
        assert d_e.original_id == '1812-A'
        assert len(c_importer.failures) == 0
        assert len(c_importer.bad_records) == 0

    def test_import_exceptions(self):
        records = [
            [u'1812-A', u'exception', u'Naderend onweer', u'data',
             u'http://www.vlaamsekunstcollectie.be/collection.aspx?p=0848cab7-2776-4648-9003-25957707491a&inv=1812-A',
             u'1', u'', u'xhtml', u'', u''],
            [u'1812-A', u'exception', u'Naderend onweer', u'representation',
             u'http://www.vlaamsekunstcollectie.be/proxy.aspx?server=62.221.199.163&port=28301&overlaytext=&overlaytextalpha=14&overlaytextfontname=verdana&overlaytextfontsize=8&overlaytextfontcolor=000000&overlaytextbackgroundcolor=cccccc&cache=yes&borderwidth=0&borderheight=0&bordercolor=999999&passepartoutwidth=6&passepartoutheight=6&passepartoutcolor=ffffff&bg=ffffff&filename=gent%2F1812-A.jpg',
             u'1', u'', u'1', u'1', u'']
            ]
        import_id = '123'
        c_importer = CSVImporter(records, import_id)
        c_importer.store()

        assert len(c_importer.failures) == 1  # Failures are for entities, all import records concern the same entity
        assert c_importer.failures == ['Entity 1812-A: UnrecognizedEntityType: exception']
        assert len(c_importer.bad_records) == 2
        assert c_importer.bad_records == records

