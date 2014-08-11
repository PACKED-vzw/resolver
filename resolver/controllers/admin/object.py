import csv, tempfile
from flask import redirect, request, render_template, flash, make_response
from resolver import app
from resolver.model import PersistentObject, Document,\
    object_types, document_types
from resolver.database import db
from resolver.controllers.admin.user import check_privilege
from resolver.forms import ObjectForm, DocumentForm
from resolver.util import log, UnicodeWriter, UnicodeReader

@app.route('/admin/object')
@check_privilege
def admin_list_persistent_objects(form=False):
    objects = PersistentObject.query.all()
    form = form if form else ObjectForm()
    return render_template("admin/objects.html", title="Admin",\
                           objects=objects, form=form)

@app.route('/admin/object', methods=["POST"])
@check_privilege
def admin_new_persistent_object():
    form = ObjectForm()
    if form.validate():
        obj = PersistentObject.query.\
              filter(PersistentObject.id == form.id.data).first()
        if obj:
            flash("ID not unique", "warning")
            return admin_list_persistent_objects(form=form)
        obj = PersistentObject(type=form.type.data,
                               title=form.title.data,
                               id=form.id.data)
        db.session.add(obj)
        db.session.commit()
        log("added a new object to the system: %s" % obj)
        # TODO: to flash or not to flash (UX)
        return redirect("/admin/object/%s" % obj.id)
    else:
        return admin_list_persistent_objects(form=form)

@app.route('/admin/object/<id>')
@check_privilege
def admin_view_persistent_object(id, form=None):
    po = PersistentObject.query.filter(PersistentObject.id == id).first()
    if po:
        documents = po.documents
        form = form if form else DocumentForm()
        return render_template("admin/object.html", title="Admin",
                               object=po, documents=documents, form=form)
    else:
        flash("Object not found!", "danger")
        return redirect("/admin/object")

@app.route('/admin/object/<id>', methods=["POST"])
@check_privilege
def admin_new_document(id):
    form = DocumentForm()
    po = PersistentObject.query.filter(PersistentObject.id == id).first()
    if not po:
        flash("Object for document not found!", "danger")
        return admin_view_persistent_objects()
    if not form.validate():
        return admin_view_persistent_object(id, form=form)
    # TODO: I assume only one instance per document type
    if form.type.data in map(lambda obj: obj.type, po.documents):
        flash("There already is a document of this type", "warning")
        return admin_view_persistent_object(id, form=form)
    document = Document(id, type=form.type.data, url=form.url.data,
                        enabled=form.enabled.data, notes=form.notes.data)
    db.session.add(document)
    db.session.commit()
    log("added a new document `%s' to the object `%s'" % (document, po))
    # TODO: to flash or not to flash (UX)
    return redirect('/admin/object/%s' % id)

@app.route('/admin/object/edit/<id>', methods=["GET", "POST"])
@check_privilege
def admin_edit_object(id):
    obj = PersistentObject.query.filter(PersistentObject.id == id).first()

    if not obj:
        flash("Object not found", "warning")
        return redirect("/admin/object")

    if request.method == 'POST':
        form = ObjectForm()

        if not form.validate():
            return render_template("admin/edit_object.html", title="Admin",
                                   object=obj, form=form)
        old = str(obj)
        obj.title = form.title.data
        obj.type = form.type.data
        obj.id = form.id.data
        db.session.commit() #commit changes to DB
        log("changed object `%s' to `%s'" % (old, obj))
        return redirect('/admin/object/%s' % obj.id)
    form = ObjectForm(request.form, obj)
    return render_template("admin/edit_object.html", title="Admin",
                           object=obj, form=form)

#@app.route('/admin/object/<int:id>', methods=["DELETE"])
@app.route('/admin/object/delete/<id>')
@check_privilege
def admin_delete_persistent_object(id):
    po = PersistentObject.query.filter(PersistentObject.id == id).first()
    if not po:
        flash("Object not found!", "danger")
    else:
        db.session.delete(po)
        db.session.commit()
        log("removed the object `%s' from the system" % po)
        flash("Object deleted succesfully!", "success")
    return redirect("/admin/object")

@app.route('/admin/csv')
@check_privilege
def admin_csv():
    return render_template('admin/csv.html', title='Admin')

@app.route('/admin/csv/import', methods=["POST"])
@check_privilege
def admin_csv_import():
    def allowed(filename):
        return ('.' in filename) and\
            (filename.rsplit('.', 1)[1].lower() == 'csv')

    file = request.files['file']

    if not file:
        flash("No file provided", "warning")
        return redirect("/admin/csv")

    if not allowed(file.filename):
        flash("File not allowed", "warning")
        return redirect("/admin/csv")

    log("is starting a CSV import session...")
    # TODO: skip first row if it includes legend (we assume no legend)?

    reader = UnicodeReader(file)
    # As this feature is mainly used for imports/edits from Excel, it is
    # possible that Excel uses `;' as a separator instead of `,' ...
    if len(ur.next()) != 7:
        file.seek(0)
        reader = UnicodeReader(file, delimiter=';')

    for id, otype, title, dtype, url, enabled, notes in reader:
        obj = PersistentObject.query.\
              filter(PersistentObject.id == id).first()
        doc = Document.query.\
              filter(Document.object_id == id).\
              filter(Document.type == dtype).\
              first()

        if not otype in object_types:
            flash("An object was encountered with an incorrect type\
            (ID: %s)" % id, "warning")
            continue

        if not dtype in document_types:
            flash("A document was encountered with an incorrect type\
            (Object ID: %s)" % id, "warning")
            continue

        if obj:
            str = "modified `%s'" % obj
            obj.id = id
            obj.type = otype
            obj.title = title
            log("%s to `%s'" % (str, obj))
        else:
            obj = PersistentObject(id, type=otype, title=title)
            db.session.add(obj)
            log("imported a new object to the system: %s" % obj)

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
            log("imported a new document `%s' for the object `%s'" %
                (doc, obj))

        db.session.commit()

    log("finished a CSV import session.")
    # TODO: redirect to objects page after import?
    flash("Data imported", "success")
    return redirect("/admin/csv")

@app.route('/admin/csv/export')
@check_privilege
def admin_csv_export():
    objects = PersistentObject.query.all()
    # I'd rather write all data to a memory stream than a file, but streams
    # require unicode and Python's csv/UnicodeWriter don't like unicode that
    # much
    file = tempfile.NamedTemporaryFile()
    writer = UnicodeWriter(file)

    #writer.writerow(['PID', 'object type', 'title', 'document type', 'URL',
    #                 'enabled', 'notes'])

    for object in objects:
        for document in object.documents:
            writer.writerow([object.id, object.type, object.title, document.type,
                             document.url, "1" if document.enabled else "0",
                             str(document.notes)])

    file.seek(0)

    response = make_response(file.read())
    response.headers["Content-Disposition"] = 'attachment; filename="export.csv"'
    response.headers["Content-Type"] = 'text/csv'

    file.close()

    return response
