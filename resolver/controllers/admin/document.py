from resolver import app
from resolver.util import log
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
    object_id = doc.object_id
    if not doc:
        flash("Document not found", "warning")
        return redirect("/admin/object")
    log("removed the document `%s' from object `%s'" %
        (doc, doc.persistent_object))
    db_session.delete(doc)
    db_session.commit()
    flash("Document deleted succesfully", "success")
    return redirect("/admin/object/%s" % object_id)

@app.route('/admin/document/edit/<int:id>', methods=["GET", "POST"])
@check_privilege
def admin_edit_document(id):
    doc = Document.query.filter(Document.id == id).first()

    if not doc:
        flash("Document not found", "warning")
        return redirect("/admin/object")

    if request.method == 'POST':
        form = DocumentForm()

        # TODO: I assume only one instance per document type
        if (form.type.data != doc.type) and\
           (form.type.data in map(lambda obj: obj.type,
                                  doc.persistent_object.documents)):
            flash("There already is a document of this type", "warning")
            return render_template("admin/edit_document.html", title="Admin",
                                   document=doc, form=form)
        old = str(doc)
        doc.enabled = form.enabled.data
        doc.type = form.type.data
        doc.url = form.url.data
        db_session.commit() #commit changes to DB
        log("changed document `%s' to `%s'" % (old, doc))
        # TODO: redirect to /admin/object instead?
        return redirect('/admin/document/%s' % id)
    form = DocumentForm(request.form, doc)
    return render_template("admin/edit_document.html", title="Admin",\
                           document=doc, form=form)
