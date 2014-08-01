from resolver import app
from resolver.model import PersistentObject, Document,\
    object_types, document_types
from resolver.database import db_session
from resolver.controllers.admin.user import check_privilege
from resolver.controllers.admin.object import *
from flask import redirect, request, render_template, flash

@app.route('/admin/document/<int:id>')
@check_privilege
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
@check_privilege
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
@check_privilege
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
@check_privilege
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
