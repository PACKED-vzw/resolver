import json
from resolver import app
from resolver.util import log
from resolver.model import PersistentObject, Document,\
    object_types, document_types
from resolver.database import db_session
from resolver.controllers.admin.user import check_privilege
from resolver.controllers.admin.object import *
from flask import redirect, request, render_template, flash

@app.route('/admin/document/<int:id>.json')
@check_privilege
def admin_view_document_json(id):
    doc = Document.query.filter(Document.id == id).first()

    if not doc:
        return json.dumps({'errors':[{'detail':'Document ID invalid'}]})

    return json.dumps({'id':doc.id,
                       'type':doc.type,
                       'url':doc.url,
                       'object':{'id':doc.object_id},
                       'enabled':doc.enabled,
                       'notes':doc.notes,
                       'persistent_uri':doc.persistent_uri})

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

@app.route('/admin/document/edit/<int:id>.json', methods=["POST"])
@check_privilege
def admin_edit_document_json(id):
    doc = Document.query.filter(Document.id == id).first()

    if not doc:
        return "Document not found"

    # We can still parse the form from the request data
    form = DocumentForm()

    if form.validate():
        if (form.type.data != doc.type) and\
           (form.type.data in map(lambda obj: obj.type,
                                  doc.persistent_object.documents)):
            return json.dumps({'errors':[{'title':'Type not unique',
                                          'detail':'There already is a document\
                                          of this type'}]})

        old = str(doc)
        doc.enabled = form.enabled.data
        doc.type = form.type.data
        doc.url = form.url.data
        doc.notes = form.notes.data
        db_session.commit() #commit changes to DB
        log("changed document `%s' to `%s'" % (old, doc))
        return json.dumps({'success':True})
    else:
        errors = []
        for type, msgs in form.errors.iteritems():
            for msg in msgs:
                errors.append({'title':type, 'detail':msg})
        return json.dumps({'errors':errors})
