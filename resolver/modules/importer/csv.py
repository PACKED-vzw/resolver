from threading import Thread
import traceback
from Queue import Queue
from resolver.modules.api.entity import EntityApi
from resolver.util import log, import_log
from resolver import app
import time


# https://www.toptal.com/python/beginners-guide-to-concurrency-and-parallelism-in-python


class CSVImporter:
    def __init__(self, records, import_id):
        # We need all the records with the same ID
        self.import_id = import_id
        self.records = records
        self.failures = []
        self.bad_records = []

    def store(self):
        e_api = EntityApi()
        try:
            entity, documents = e_api.create_from_rows(self.records, self.import_id)
        except Exception as e:
            a_exc = traceback.format_exc().splitlines()
            error_msg = 'Entity {0}: {1}'.format(self.records[0][0], a_exc[-1])
            self.failures.append(error_msg)
            self.bad_records += self.records
            app.logger.error(error_msg)
            e_api.rollback()
        else:
            import_log(self.import_id, 'Added/updated PID {0}'.format(entity.id))
