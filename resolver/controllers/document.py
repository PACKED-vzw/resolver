import json
from resolver import app
from resolver.util import log
from resolver.model import Entity, Document, entity_types, document_types
from resolver.forms import DocumentForm
from resolver.database import db
from resolver.controllers.user import check_privilege
from flask import redirect, request, render_template, flash

@app.route('/resolver/document/<int:id>.json')
@check_privilege
def admin_view_document_json(id):
    doc = Document.query.filter(Document.id == id).first()

    if not doc:
        return json.dumps({'errors':[{'detail':'Document ID invalid'}]})

    # TODO: add method to Document to create dict?
    return json.dumps({'id':doc.id,
                       'type':doc.type,
                       'url':doc.url,
                       'entity':{'id':doc.entity_id},
                       'enabled':doc.enabled,
                       'notes':doc.notes,
                       'persistent_uri':doc.persistent_uri,
                       'resolves':doc.resolves})

@app.route('/resolver/document/delete/<int:id>')
@check_privilege
def admin_delete_document(id):
    doc = Document.query.filter(Document.id == id).first()
    entity_id = doc.entity_id
    if not doc:
        flash("Document not found", "warning")
        return redirect("/resolver/entity")
    log("removed the document `%s' from entity `%s'" %
        (doc, doc.entity))
    db.session.delete(doc)
    db.session.commit()
    flash("Document deleted succesfully", "success")
    return redirect("/resolver/entity/%s" % entity_id)

@app.route('/resolver/document/edit/<int:id>.json', methods=["POST"])
@check_privilege
def admin_edit_document_json(id):
    doc = Document.query.filter(Document.id == id).first()

    if not doc:
        return "Document not found"

    # We can still parse the form from the request data
    form = DocumentForm()

    if form.validate():
        if (form.type.data != doc.type) and\
           (form.type.data in map(lambda ent: ent.type,
                                  doc.entity.documents)):
            return json.dumps({'errors':[{'title':'Type not unique',
                                          'detail':'There already is a document\
                                          of this type'}]})

        old = str(doc)
        doc.enabled = form.enabled.data
        doc.type = form.type.data
        doc.url = form.url.data
        doc.notes = form.notes.data
        db.session.commit() #commit changes to DB
        log("changed document `%s' to `%s'" % (old, doc))
        return json.dumps({'success':True})
    else:
        errors = []
        for type, msgs in form.errors.iteritems():
            for msg in msgs:
                errors.append({'title':type, 'detail':msg})
        return json.dumps({'errors':errors})
