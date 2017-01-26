import time
from rq import Queue
import redis

from resolver.modules.importer.csv import CSVImporter
from resolver.util import UnicodeReader
from resolver import app

# Also: check for failed queue


class CSVRedis:
    def __init__(self, csv_filename):
        self.import_id = str(time.time())
        self.conn = redis.Redis()
        self.queue = Queue(connection=self.conn)
        self.failed = Queue('failed', connection=self.conn)
        csv_file = open(csv_filename, 'r')
        csv_fh = UnicodeReader(csv_file)
        rows = []
        for line in csv_fh:
            rows.append(line)
        self.job = self.queue.enqueue_call(
            func=redis_import,
            args=(rows, self.import_id),
            timeout=3600
        )


def redis_import(rows, import_id):
    row_pack = []
    bad_records = []
    failures = []
    header = rows.pop(0)
    current = [None]
    i = 0
    for row in rows:
        if row[0] == current[0]:
            row_pack.append(row)
            current = row
        else:
            if len(row_pack) > 0:
                i += 1
                app.logger.info('Enqueuing {0}.'.format(str(row_pack[0][0])))
                c = CSVImporter(records=row_pack, import_id=import_id)
                c.store()
                bad_records += c.bad_records
                failures += c.failures
            row_pack = [row]
            current = row
    return bad_records, failures
