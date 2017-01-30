import sys
from time import sleep
from resolver.controllers.csv import file_allowed, write_bad_records, import_file
from resolver.modules.importer.csv_redis import CSVRedisWrapper
from resolver import app


def main_legacy():
    if len(sys.argv) != 2 or not file_allowed(sys.argv[1]):
        print("Please provide a csv file as argument")
        exit(1)

    try:
        file = open(sys.argv[1])
        import_id, rows, count_pids, failures, bad_records = import_file(file)

        if failures:
            path = write_bad_records(bad_records)
            print("There were some errors whilst importing the dataset:")
            for failure in failures:
                print("PID %s: %s" % (failure[0], failure[1]))
            print("")
            print("Bad records have been written to: %s" % path)
            print("-----------------------")

        print("Imported %s rows with %s different PIDs" % (rows, count_pids))
        print("An import log can be found at %s/resolver/log/import/%s" % (app.config['BASE_URL'], import_id))

    except IOError:
        print("Could not open file!")
        exit(2)


def main():
    if len(sys.argv) != 2 or not file_allowed(sys.argv[1]):
        print('Please provide a CSV file as an argument.')
        exit(1)

    try:
        fh = open(sys.argv[1])
        csv_wrapper = CSVRedisWrapper()
        csv_wrapper.csv_import(csv_fileobj=fh)

        print('Job {0}: Started'.format(csv_wrapper.job.id))

        while csv_wrapper.finished() is False:
            if csv_wrapper.failed() is True:
                print('Job {0}: Failed'.format(csv_wrapper.job.id))
                exit(3)
                break
            print('Job {0}: Running'.format(csv_wrapper.job.id))
            sleep(5)

        print('Job {0}: Finished'.format(csv_wrapper.job.id))

        if csv_wrapper.failures():
            path = write_bad_records(csv_wrapper.bad_records())
            print('Job {0} encountered some errors:'.format(csv_wrapper.job.id))
            for failure in csv_wrapper.failures():
                print('PID {0}: {1}'.format(failure[0], failure[1]))
            print('')
            print('Bad records have been written to: {0}'.format(path))
            print('-----------------------')

        print('An import log can be found at {0}/resolver/log/import/{1}'.format(app.config['BASE_URL'],
                                                                                 csv_wrapper.import_id()))

    except IOError:
        print('Failed to open file {0}.'.format(sys.argv[1]))
        exit(2)


if __name__ == '__main__':
    if app.config['USE_REDIS'] is True:
        main()
    else:
        main_legacy()
