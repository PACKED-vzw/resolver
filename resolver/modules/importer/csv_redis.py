import time
from rq import Queue
import redis

from resolver.modules.importer.csv import CSVImporter
from resolver.util import UnicodeReader
from resolver import app


class RedisJobMissing(Exception):
    pass

# Also: check for failed queue


class CSVRedisWrapper:
    def __init__(self, job=None):
        self.connection = redis.Redis(
            host=app.config['REDIS_HOST'],
            port=app.config['REDIS_PORT']
        )
        self.q_queue = Queue(connection=self.connection)
        self.q_failed = Queue(connection=self.connection)
        self.__job = job

    def csv_import(self, csv_fileobj):
        c = CSVRedis(csv_fileobj=csv_fileobj, queue=self.q_queue)
        self.__job = c.job

    def get_job(self, job_id):
        self.__job = self.q_queue.fetch_job(job_id)
        if self.__job is None:
            raise RedisJobMissing()

    @property
    def job(self):
        return self.__job

    def finished(self):
        if self.__job is None:
            raise RedisJobMissing()
        if self.__job.result is not None:
            return True
        return False

    def failed(self):
        if self.__job is None:
            raise RedisJobMissing()
        try:
            if self.__job.failed is True:
                return True
        except AttributeError:
            return False
        return False

    def bad_records(self):
        if self.__job is None:
            raise RedisJobMissing()
        if self.finished():
            return self.job.result[0]
        return []

    def failures(self):
        if self.__job is None:
            raise RedisJobMissing()
        if self.finished():
            return self.job.result[1]
        return []

    def import_id(self):
        if self.__job is None:
            raise RedisJobMissing()
        return self.job.meta['import_id']


class CSVRedis:
    def __init__(self, csv_fileobj, queue):
        self.import_id = str(time.time())
        self.queue = queue

        csv_fh = UnicodeReader(csv_fileobj)

        # Redis/cPickle can't handle open file objects, so convert to array
        rows = []
        for line in csv_fh:
            rows.append(line)

        self.job = self.queue.enqueue_call(
            func=redis_import,
            args=(rows, self.import_id),
            timeout=app.config['REDIS_TIMEOUT']
        )
        self.job.meta['import_id'] = self.import_id
        self.job.save()


def redis_import(rows, import_id):
    row_pack = []
    bad_records = []
    failures = []
    header = rows.pop(0)
    current = [None]
    i = 0
    for row in rows:
        # If they have the same original_ID (row[0]), they are data/representations for the same entity
        # and must be put together in the row_pack for CSVImporter()
        if row[0] == current[0]:
            row_pack.append(row)
            current = row
        else:
            # Do'nt try to import a row_pack that's empty
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
