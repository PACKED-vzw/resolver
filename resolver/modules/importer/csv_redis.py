import time
from rq import Queue
import redis

from resolver.modules.importer.csv import CSVImporter
from resolver.util import UnicodeReader
from resolver import app


class CSVRedis:
    def __init__(self, csv_file):
        self.import_id = str(time.time())
        self.conn = redis.Redis(host='192.168.41.99')
        self.queue = Queue(connection=self.conn)
        self.failed = Queue('failed', connection=self.conn)
        csv_fh = UnicodeReader(csv_file)
        rows = []
        for line in csv_fh:
            rows.append(line)
        self.job = self.queue.enqueue_call(
            func=redis_import,
            args=(rows, self.import_id)
        )


def redis_import(rows, import_id):
    row_pack = []
    bad_records = []
    failures = []
    header = rows.pop(0)
    current = [None]
    i = 0
    for row in rows:
        print(row)
        if i == 1:
            break
        if row[0] == current[0]:
            row_pack.append(row)
            current = row
        else:
            if len(row_pack) > 0:
                i += 1
                print('Enqueuing {0}.'.format(str(row_pack[0][0])))
                c = CSVImporter(records=row_pack, import_id=import_id)
                c.store()
                bad_records.append(c.bad_records)
                failures.append(c.failures)
            row_pack = [row]
            current = row
    return bad_records, failures
