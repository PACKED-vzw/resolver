from resolver import app
from resolver.controllers import csv
import sys


if __name__ == '__main__':
    if len(sys.argv) != 2 or not csv.file_allowed(sys.argv[1]):
        print "Please provide a csv file as argument"
        exit()

    try:
        file = open(sys.argv[1])
        import_id, rows, count_pids, failures, bad_records = csv.import_file(file)

        if failures:
            path = csv.write_bad_records(bad_records)
            print "There were some errors whilst importing the dataset:"
            for failure in failures:
                print "PID %s: %s" % (failure[0], failure[1])
            print ""
            print "Bad records have been written to: %s" % path
            print "-----------------------"

        print "Imported %s rows with %s different PIDs" % (rows, count_pids)
        print "An import log can be found at %s/resolver/log/import/%s" % (app.config['BASE_URL'], import_id)

    except IOError:
        print "Could not open file!"
        exit()