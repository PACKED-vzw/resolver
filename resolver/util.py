# -*- coding: utf-8-unix -*-
import csv, codecs, cStringIO, re
from unidecode import unidecode
from flask import session
from resolver import app

def log(action):
    app.logger.info("Resolver: user `%s' %s", session.get('username'), action)

_clean_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^`{|}]+')
def cleanID(ID):
    patterns = [
        # Exceptions
        ('- ',''),(' -',''),('\)+$',''),('\]+$', ''),('\°+$', ''),
        # Simple replacements
        ('\.','_'),(' ','_'),('\(','_'),('\)','_'),('\[','_'),('\]','_'),
        ('\/','_'),('\?','_'),(',','_'),('&','_'),('\+','_'),('°','_'),
        # Replace 1 or more underscores by a single underscore
        ('_+', '_')]
    partial = reduce(lambda str, t: re.sub(t[0], t[1], str),
                     patterns,
                     ID)
    # For safety, let's give it another scrub.
    result = []
    for word in _clean_re.split(partial):
        result.extend(unidecode(word).split())

    return unicode(''.join(result))

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
