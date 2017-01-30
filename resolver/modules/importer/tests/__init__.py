from flask_testing import TestCase
import resolver
from resolver.database import init_db, db
import os


class ImporterTest(TestCase):

    def create_app(self):
        resolver.app.config['TESTING'] = True
        return resolver.app

    def setUp(self):
        init_db()

    def tearDown(self):
        self.clear()
        db.drop_all()
        db.session.commit()

    def clear(self):
        db.session.remove()
        db.session.commit()
