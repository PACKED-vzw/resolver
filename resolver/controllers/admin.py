from resolver import app
from resolver.model import PersistentObject, Document,\
    object_types, document_types
from resolver.database import db_session
from flask import redirect, request, render_template, flash

# TODO: Edit titles everywhere

@app.route('/')
def index():
    return redirect('/admin')

@app.route('/admin')
def admin_index():
    #return render_template("admin/index.html", title="Admin", item="Hello, world!")
    return redirect('/admin/object')

@app.route('/admin/object')
def admin_list_persistent_objects():
    objects = PersistentObject.query.all()
    return render_template("admin/objects.html", title="Admin",\
                           objects=objects, types=object_types)

@app.route('/admin/object/<int:id>')
def admin_view_persistent_object(id):
    po = PersistentObject.query.filter(PersistentObject.id == id).first()

    if po:
        documents = po.documents
        return render_template("admin/object.html", title="Admin",
                               object=po, documents=documents,\
                               types=document_types)
    else:
        flash("Object not found!", "danger")
        return redirect("/admin/object")

#@app.route('/admin/object/<int:id>', methods=["DELETE"])
@app.route('/admin/object/delete/<int:id>')
def admin_delete_persistent_object(id):
    po = PersistentObject.query.filter(PersistentObject.id == id).first()

    if not po:
        flash("Object not found!", "danger")
    else:

        for doc in po.documents:
            db_session.delete(doc)

        db_session.delete(po)
        db_session.commit()

        flash("Object deleted succesfully!", "success")

    return redirect("/admin/object")

@app.route('/admin/object', methods=["POST"])
def admin_new_persistent_object():
    if request.form['type'] in object_types:
        obj = PersistentObject(type=request.form['type'],
                               title=request.form['title'])
        db_session.add(obj)
        db_session.commit()
        # TODO: flash or not? (UX)
        return redirect('/admin/object/%s' % obj.id)
    else:
        flash("Type of object not allowed", "danger")
        return admin_view_persistent_objects()

@app.route('/admin/object/edit/<int:id>', methods=["GET", "POST"])
def admin_edit_object(id):
    obj = PersistentObject.query.filter(PersistentObject.id == id).first()

    if not obj:
        flash("Object not found", "warning")
        return redirect("/admin/object")

    if request.method == 'POST':
        if not(request.form['type'] in object_types):
            flash("Type of object not allowed", "danger")
            render_template("admin/edit_object.html", title="Admin",\
                            object=obj, types=object_types)

        # TODO: Check form (WTForms?)
        obj.title = request.form['title']
        obj.type = request.form['type']
        db_session.commit() #commit changes to DB

        return redirect('/admin/object/%s' % id)

    return render_template("admin/edit_object.html", title="Admin",\
                           object=obj, types=object_types)

@app.route('/admin/document/<int:id>')
def admin_view_document(id):
    doc = Document.query.filter(Document.id == id).first()
    po = doc.persistent_object

    if not doc:
        flash("Document not found", "warning")
        return redirect("/admin/object")

    return render_template("admin/document.html", title="Admin",\
                           document=doc, po=po)

#@app.route('/admin/document/<int:id>', methods=["DELETE"])
@app.route('/admin/document/delete/<int:id>')
def admin_delete_document(id):
    doc = Document.query.filter(Document.id == id).first()

    if not doc:
        flash("Document not found", "warning")
        return redirect("/admin/object")

    object_id = doc.object_id

    db_session.delete(doc)
    db_session.commit()

    flash("Document deleted succesfully", "success")

    return redirect("/admin/object/%s" % object_id)

@app.route('/admin/document/<int:id>', methods=["POST"])
def admin_new_document(id):
    po = PersistentObject.query.filter(PersistentObject.id == id).first()

    if not po:
        flash("Object for document not found!", "danger")
        return admin_view_persistent_objects()

    if not(request.form['type'] in document_types):
        flash("Type of document not allowed", "danger")
        return admin_view_persistent_object(id)

    # TODO: I assume only one instance per document type
    if request.form['type'] in map(lambda obj: obj.type, po.documents):
        flash("There already is a document of this type", "warning")
        return admin_view_persistent_object(id)

    # TODO: Check if URL is not empty and sane (WTForms?)
    document = Document(id, type=request.form['type'], url=request.form['url'])
    db_session.add(document)
    db_session.commit()

    # TODO: to flash or not to flash (UX)

    return redirect('/admin/object/%s' % id)

@app.route('/admin/document/edit/<int:id>', methods=["GET", "POST"])
def admin_edit_document(id):
    doc = Document.query.filter(Document.id == id).first()

    if not doc:
        flash("Document not found", "warning")
        return redirect("/admin/object")

    if request.method == 'POST':
        if not(request.form['type'] in document_types):
            flash("Type of document not allowed", "danger")
            #return admin_view_persistent_object(id)
            return render_template("admin/edit_document.html", title="Admin",\
                                   document=doc, types=document_types)

        # TODO: I assume only one instance per document type
        if (request.form['type'] != doc.type) and\
           (request.form['type'] in map(lambda obj: obj.type,\
                                        doc.persistent_object.documents)):
            flash("There already is a document of this type", "warning")
            return render_template("admin/edit_document.html", title="Admin",\
                                   document=doc, types=document_types)

        # TODO: Check form (WTForms?)
        doc.enabled = 'enabled' in request.form
        doc.type = request.form['type']
        doc.url = request.form['url']
        db_session.commit() #commit changes to DB

        return redirect('/admin/document/%s' % id)

    return render_template("admin/edit_document.html", title="Admin",\
                           document=doc, types=document_types)

@app.route('/admin/csv', methods=["GET", "POST"])
def admin_csv_import():
    return "TODO"
