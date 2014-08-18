import csv, tempfile
from flask import request, render_template, flash, make_response, redirect
from resolver import app
from resolver.model import Entity, Document, entity_types, document_types
from resolver.database import db
from resolver.controllers.user import check_privilege
from resolver.util import log, UnicodeWriter, UnicodeReader

@app.route('/resolver/csv')
@check_privilege
def admin_csv():
    return render_template('resolver/csv.html', title='CSV')

@app.route('/resolver/csv/import', methods=["POST"])
@check_privilege
def admin_csv_import():
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

    log("is starting a CSV import session...")
    # TODO: skip first row if it includes legend (we assume there is a legend)?

    reader = UnicodeReader(file)
    # As this feature is mainly used for imports/edits from Excel, it is
    # possible that Excel uses `;' as a separator instead of `,' ...
    if len(reader.next()) != 7:
        file.seek(0)
        reader = UnicodeReader(file, delimiter=';')
        reader.next() # Skip legend

    for id, etype, title, dtype, url, enabled, notes in reader:
        ent = Entity.query.\
              filter(Entity.id == id).first()
        doc = Document.query.\
              filter(Document.entity_id == id).\
              filter(Document.type == dtype).\
              first()

        if not etype in entity_types:
            flash("An entity was encountered with an incorrect type\
            (ID: %s)" % id, "warning")
            continue

        if not dtype in document_types:
            flash("A document was encountered with an incorrect type\
            (Entity ID: %s)" % id, "warning")
            continue

        if ent:
            str = "modified `%s'" % ent
            ent.id = id
            ent.type = etype
            ent.title = title
            log("%s to `%s'" % (str, ent))
        else:
            ent = Entity(id, type=etype, title=title)
            db.session.add(ent)
            log("imported a new entity to the system: %s" % ent)

        if doc:
            str = "modified `%s'" % doc
            doc.enabled = (enabled == '1')
            doc.type = dtype
            doc.url = url
            doc.notes = notes
            log("%s to `%s'" % (str, doc))
        else:
            # TODO: Make enabled more idiot-proof
            doc = Document(id, dtype, url, enabled=='1', notes)
            db.session.add(doc)
            log("imported a new document `%s' for the entity `%s'" %
                (doc, ent))

        db.session.commit()

    log("finished a CSV import session.")
    # TODO: redirect to objects page after import?
    flash("Data imported", "success")
    return redirect("/resolver/csv")

@app.route('/resolver/csv/export')
@check_privilege
def admin_csv_export():
    entities = Entity.query.all()
    # I'd rather write all data to a memory stream than a file, but streams
    # require unicode and Python's csv/UnicodeWriter don't like unicode that
    # much
    file = tempfile.NamedTemporaryFile()
    writer = UnicodeWriter(file)

    writer.writerow(['PID', 'entity type', 'title', 'document type', 'URL',
                     'enabled', 'notes'])

    for entity in entities:
        for document in entity.documents:
            writer.writerow([entity.id, entity.type, entity.title, document.type,
                             document.url, "1" if document.enabled else "0",
                             str(document.notes)])

    file.seek(0)

    response = make_response(file.read())
    response.headers["Content-Disposition"] = 'attachment; filename="export.csv"'
    response.headers["Content-Type"] = 'text/csv'

    file.close()

    return response
