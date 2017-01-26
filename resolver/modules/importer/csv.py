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


class CSVPoll(Thread):
    def __init__(self, queue, import_id, failures, bad_records):
        Thread.__init__(self)
        self.queue = queue
        self.import_id = import_id
        self.failures = failures
        self.bad_records = bad_records

    def run(self):
        while True:
            records = self.queue.get()
            c = CSVImporter(records=records, import_id=self.import_id)
            c.store()
            if len(c.failures) > 0:
                print('Failures')
                print(c.failures)
            if len(c.bad_records) > 0:
                print('Bad records')
                print(c.bad_records)
            self.failures.put(c.failures)
            self.bad_records.put(c.bad_records)
            self.queue.task_done()


class CSVMultiThread:
    def __init__(self, csv_fh):
        ts = time.time()
        app.logger.info('Started CSV import at {0}.'.format(str(ts)))
        self.queue = Queue()
        self.failures = Queue()
        self.bad_records = Queue()
        self.import_id = str(time.time())
        for x in range(8):
            worker = CSVPoll(self.queue, self.import_id, self.failures, self.bad_records)
            worker.daemon = True
            worker.start()

        row_pack = []
        header = csv_fh.next()
        current = [None]
        i = 0
        for row in csv_fh:
            #if i == 1:
            #    break
            if row[0] == current[0]:
                row_pack.append(row)
                current = row
            else:
                if len(row_pack) > 0:
                    i += 1
                    app.logger.info('Enqueuing {0}.'.format(str(row_pack[0][0])))
                    self.queue.put(row_pack)
                row_pack = [row]
                current = row
        self.queue.join()
        failures = [f for f in self.failures.get()]
        bad_records = [b for b in self.bad_records.get()]
        print(failures)
        print(bad_records)
        te = time.time()
        app.logger.info('Ended CSV import at {0}. Took {1}.'.format(str(te), str(te - ts)))
