from resolver.modules.importer.csv_redis import CSVRedis
from resolver import app
import time


csv_filename = '/vagrant/large_csv.csv'

c = CSVRedis(csv_filename)

while c.job.result is None:
    print('Waiting for result')
    time.sleep(5)

bad_records = open('/vagrant/bad.csv', 'w')
failures = open('/vagrant/failures.csv', 'w')

bad_records.write('Record')
failures.write('Failure')

for bad in c.job.result[0]:
    bad_records.write('"{0}"\n'.format(bad))

for fail in c.job.result[1]:
    failures.write('"{0}"\n'.format(fail))

bad_records.close()
failures.close()
