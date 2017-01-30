from time import sleep
from resolver.modules.importer.tests import ImporterTest
from resolver.modules.importer.csv_redis import CSVRedisWrapper
from resolver.modules.api.entity import EntityApi
from resolver.model import Entity, Data, Document, Representation


class RedisTest(ImporterTest):

    def test_import(self):
        r = CSVRedisWrapper()
        f = open('resolver/modules/importer/tests/csv.csv', 'r')
        r.csv_import(f)
        assert r.job is not None
        assert r.failed() is False
        while r.finished() is False and r.failed() is False:
            sleep(5)
        assert len(Entity.query.all()) == 6
        assert len(Data.query.all()) == 6
        assert len(Representation.query.all()) == 6
