import csv, tempfile, cStringIO
from flask import request, render_template, flash, make_response, redirect
from resolver import app
from resolver.model import Entity, Document, Data, Representation,\
    entity_types, document_types
from resolver.database import db
from resolver.controllers.user import check_privilege
from resolver.util import log, UnicodeWriter, UnicodeReader, cleanID

@app.route('/resolver/csv')
@check_privilege
def admin_csv():
    return render_template('resolver/csv.html', title='Import & Export')

@app.route('/resolver/csv/import', methods=["POST"])
@check_privilege
def admin_csv_import():
    # TODO: Function too big!
    # TODO: logging?
    def allowed(filename):
        return ('.' in filename) and\
            (filename.rsplit('.', 1)[1].lower() == 'csv')

    file = request.files['file']

    if not file:
        flash("No file provided", "warning")
        return redirect("/resolver/csv")

    if not allowed(file.filename):
        flash("File not allowed", "warning")
        return redirect("/resolver/csv")

    #log("is starting a CSV import session...")

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
    for record in reader:
        id = record[0]
        # Skip wrong types now
        if not record[1] in entity_types:
            failures.append((id, "Wrong entity type `%s'" % record[1]))
            continue
        if not record[3] in document_types:
            failures.append((id, "Wrong document type `%s'" % record[3]))
            continue

        if records.get(id, False):
            records[id].append(record)
        else:
            records[id] = [record]

    for id, record_list in records.iteritems():
        clean_id = cleanID(id)
        ent = Entity.query.\
              filter(Entity.id == clean_id).first()
        if ent:
            if not ent.original_id == id:
                failures.append((id, "PID collision with `%s'" % ent.original_id))
                continue
        else:
            ent = Entity(id)
            db.session.add(ent)
            db.session.flush()
            log(ent.id, "Added entity `%s'" % ent)

        id = ent.id
        for record in record_list:
            ent.title = record[2]
            ent.type = record[1]

            url = record[4] if record[4]!='None' else ''

            if record[3] == 'data':
                doc = Data.query.filter(Data.format == record[7],
                                        Document.entity_id == id).first()
                if doc:
                    doc.url = url
                    doc.enabled = record[5]
                    doc.notes = record[6]
                else:
                    doc = Data(id, record[7], url=url, enabled=record[5],
                               notes=record[6])
                    db.session.add(doc)
                    log(id, "Added data document `%s'" % doc)
            elif record[3] == 'representation':
                doc = Representation.query.\
                      filter(Document.entity_id == id,
                             Representation.order == record[9]).first()
                if doc:
                    doc.url = url
                    doc.enabled = record[5]
                    doc.notes = record[6]
                else:
                    doc = Representation(id, record[9], url=url,
                                         enabled=record[5], notes=record[6])
                    db.session.add(doc)
                    log(id, "Added representation document `%s'" % doc)

                reference = True if record[8] == '1' else False
                if reference:
                    ref = Representation.query.\
                          filter(Document.entity_id == id,
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
        flash("There were some errors during import", 'warning')
        return render_template('resolver/csv.html', title='Import & Export',
                               failures=failures)

    flash("Import succesful", 'success')
    return redirect("/resolver/entity")

@app.route('/resolver/csv/export')
@check_privilege
def admin_csv_export():
    entities = Entity.query.all()
    file = cStringIO.StringIO()
    writer = UnicodeWriter(file)
    writer.writerow(['PID', 'entity type', 'title', 'document type', 'URL',
                     'enabled', 'notes', 'format', 'reference', 'order'])
    for entity in entities:
        for document in entity.documents:
            if type(document) == Data:
                writer.writerow([entity.id, entity.type, entity.title, 'data',
                                 str(document.url),
                                 '1' if document.enabled else '0',
                                 str(document.notes),
                                 document.format, '', ''])
            else:
                writer.writerow([entity.id, entity.type, entity.title,
                                 'representation',
                                 str(document.url),
                                 '1' if document.enabled else '0',
                                 str(document.notes),
                                 '',
                                 '1' if document.reference else '0',
                                 str(document.order)])

    file.seek(0)
    response = make_response(file.read())
    response.headers["Content-Disposition"] = 'attachment; filename="export.csv"'
    response.headers["Content-Type"] = 'text/csv'
    file.close()
    return response
