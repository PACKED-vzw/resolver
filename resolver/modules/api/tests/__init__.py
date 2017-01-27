from flask_testing import TestCase
import resolver
from resolver.database import init_db, db
import os


class ApiTest(TestCase):

    def create_app(self):
        resolver.app.config['TESTING'] = True
        return resolver.app

    def setUp(self):
        init_db()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.session.commit()

    def t_create(self, input_data_max, input_data_min, db_class, api_class):
        e = api_class().create(input_data_max)
        assert e in db.session
        self.assertIsInstance(e, db_class)
        e_min = api_class().create(input_data_min)
        assert e_min in db.session
        return e

    def t_read(self, api_class, input_data):
        e = api_class().create(input_data)
        e_r = api_class().read(e.id)
        assert e_r == e
        return e_r

    def t_update(self, api_class, input_data, updated_data):
        e = api_class().create(input_data)
        e_u = api_class().update(e.id, updated_data)
        e_r = api_class().read(e.id)
        for key in updated_data:
            assert e_r[key] == updated_data[key]
        return e_r

    def t_delete(self, api_class, input_data):
        e = api_class().create(input_data)
        assert api_class().delete(e.id) is True
        assert e not in db.session

    def t_list(self, api_class, input_data):
        e = api_class().create(input_data)
        e_list = api_class().list()
        assert e in e_list
