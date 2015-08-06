import csv, tempfile, cStringIO, time
from flask import request, render_template, flash, make_response, redirect, session
from resolver import app
from resolver.model import Entity, Document, Data, Representation,\
    entity_types, document_types, data_formats
from resolver.database import db
from resolver.controllers.user import check_privilege
from resolver.util import log, UnicodeWriter, UnicodeReader, cleanID, import_log
from tempfile import NamedTemporaryFile

_csv_header = ['PID', 'entity type', 'title', 'document type', 'URL',
               'enabled', 'notes', 'format', 'reference', 'order']

@app.route('/resolver/csv')
@check_privilege
def admin_csv():
    return render_template('resolver/csv.html', title='Import & Export')


def file_allowed(filename):
    return ('.' in filename) and \
           (filename.rsplit('.', 1)[1].lower() == 'csv')


# TODO: script for imports
@app.route('/resolver/csv/import', methods=["POST"])
@check_privilege
def admin_csv_import():
    # First, we go over the list of all records and gather them in a dictionary, indexed on the PID.
    # Afterwards, for each PID, we check if the PID is already in the database or not
    # - If it isn't: the new entity is created using the data from the first record in the CSV file
    # - If it is (no collision): the entity is updated with the data from the first record in the CSV file
    # - If it is (collision): error!
    # Data documents are updated iff there is a document of the same format
    # Representation documents are updated iff there is a document with the same order

    # TODO: Function too big!
    # TODO: logging?

    # Create id for the import logging function (id = unique identifier of this import action)
    import_id = str(time.time())
    rows = 0
    count_pids = 0

    file = request.files['file']

    if not file:
        flash("No file provided", "warning")
        return redirect("/resolver/csv")

    if not file_allowed(file.filename):
        flash("File not allowed", "warning")
        return redirect("/resolver/csv")

    reader = UnicodeReader(file)
    # NOTE: we always assume the first row is a header
    # As this feature is mainly used for imports/edits from Excel, it is
    # possible that Excel uses `;' as a separator instead of `,' ...
    if len(reader.next()) != 10:
        file.seek(0)
        reader = UnicodeReader(file, delimiter=';')
        reader.next() # Skip header again

    records = {}
    failures = []
    bad_records = []
    for record in reader:
        id = record[0]
        # Skip wrong types now
        # TODO: do we actually fail on importing a wrong type?
        if not record[1] in entity_types:
            failures.append((id, "Wrong entity type `%s'" % record[1]))
            bad_records.append(record)
            continue
        if not record[3] in document_types:
            failures.append((id, "Wrong document type `%s'" % record[3]))
            bad_records.append(record)
            continue

        rows += 1
        if records.get(id, False):
            records[id].append(record)
            import_log(import_id, "Appended document to PID %s" % id)
        else:
            records[id] = [record]
            count_pids += 1
            import_log(import_id, "Added new PID %s" % id)

    for id, record_list in records.iteritems():
        clean_id = cleanID(id)
        ent = Entity.query.\
              filter(Entity.id == clean_id).first()
        if ent:
            if not ent.original_id == id:
                failures.append((id, "PID collision with `%s'" % ent.original_id))
                bad_records += record_list
                continue
        else:
            ent = Entity(id)
            db.session.add(ent)
            db.session.flush()
            log(ent.id, "Added entity `%s'" % ent)

        ent.title = record_list[0][2]
        ent.type = record_list[0][1]

        for record in record_list:
            url = record[4] if record[4] != 'None' else ''
            enabled = record[5] == '1'

            if record[3] == 'data':
                if not(record[7] and record[7] in data_formats):
                    failures.append((id, "Format missing or invalid for PID `%s'" % ent.id))
                    bad_records.append(record)
                    continue
                doc = Data.query.filter(Data.format == record[7],
                                        Document.entity_id == ent.id).first()
                if doc:
                    doc.url = url
                    doc.enabled = enabled
                    doc.notes = record[6]
                else:
                    doc = Data(ent.id, record[7], url=url, enabled=enabled,
                               notes=record[6])
                    db.session.add(doc)
                    log(id, "Added data document `%s'" % doc)
            elif record[3] == 'representation':
                doc = Representation.query.\
                      filter(Document.entity_id == ent.id,
                             Representation.order == record[9]).first()
                if doc:
                    doc.url = url
                    doc.enabled = enabled
                    doc.notes = record[6]
                else:
                    if record[9] and record[9] != "":
                        order = int(record[9])
                    else:
                        order = Representation.query\
                            .filter(Document.entity_id == ent.id).count() + 1

                    doc = Representation(ent.id, order, url=url,
                                         enabled=enabled, notes=record[6])
                    db.session.add(doc)
                    log(id, "Added representation document `%s'" % doc)

                reference = record[8] == '1'
                if reference:
                    ref = Representation.query.\
                          filter(Document.entity_id == ent.id,
                                 Representation.reference == True).first()
                    if ref:
                        ref.reference = False

                    doc.reference = True

            db.session.flush()

    for id in records:
        reps = Representation.query.\
               filter(Document.entity_id == id).\
               order_by(Representation.order.asc()).all()
        i = 1
        has_reference = False
        for rep in reps:
            rep.order = i
            i += 1
            has_reference = rep.reference

        if (not has_reference) and i>1:
            reps[0].reference = True

    db.session.commit()
    if failures:
        session['bad_records'] = write_bad_records(bad_records)
        flash("There were some errors during import", 'warning')
        return render_template('resolver/csv.html', title='Import & Export',
                               failures=failures)

    flash('Import successful', 'success')
    return render_template ('resolver/csv.html', title="Import & Export",
                            import_log_id=import_id, rows=rows, count_pids=count_pids)


def write_bad_records(records):
    file = NamedTemporaryFile(delete=False)
    writer = UnicodeWriter(file)
    writer.writerow(_csv_header)
    for record in records:
        writer.writerow(record)
    file.close()
    print file.name
    return file.name


@app.route('/resolver/csv/records')
def get_bad_records():
    if not session.get('bad_records'):
        flash("File not found", 'warning')
        return redirect("/resolver/csv")
    file = open(session.get('bad_records'))
    response = make_response(file.read())
    response.headers["Content-Disposition"] = 'attachment; filename="export.csv"'
    response.headers["Content-Type"] = 'text/csv'
    file.close()
    return response


@app.route('/resolver/csv/export')
@check_privilege
def admin_csv_export():
    # TODO: Fix all the 'None' in export
    entities = Entity.query.all()
    file = cStringIO.StringIO()
    writer = UnicodeWriter(file)
    writer.writerow(_csv_header)
    # TODO add column persistent_link (as separate export?)
    # TODO ignore column persistent_link while importing (but column is not required)
    for entity in entities:
        for document in entity.documents:
            if type(document) == Data:
                writer.writerow([entity.id, entity.type, entity.title, 'data',
                                 unicode(document.url) if document.url else '',
                                 '1' if document.enabled else '0',
                                 unicode(document.notes) if document.notes else '',
                                 document.format, '', ''])
            else:
                writer.writerow([entity.id, entity.type, entity.title,
                                 'representation',
                                 unicode(document.url) if document.url else '',
                                 '1' if document.enabled else '0',
                                 unicode(document.notes) if document.notes else '',
                                 '',
                                 '1' if document.reference else '0',
                                 unicode(document.order)])

    file.seek(0)
    response = make_response(file.read())
    response.headers["Content-Disposition"] = 'attachment; filename="badrecords.csv"'
    response.headers["Content-Type"] = 'text/csv'
    file.close()
    return response


@app.route('/resolver/csv/purge')
@check_privilege
def purge_database():
    Entity.query.delete()
    db.session.commit()
    flash("Database has been purged", "success")
    return redirect('/resolver/csv')