from resolver import app
from resolver.model import PersistentObject, Document
from flask import redirect

@app.route('/collection')
def collection():
    return 'Error: ID required'

@app.route('/collection/<int:id>')
def view_object(id):
    po = PersistentObject.query.filter(PersistentObject.id == id).first()

    if not po:
        return "Not Found"

    # TODO: Implement default action
    docs = po.documents_by_type
    if docs["data"]:
        return redirect(docs["data"].url, code=303)

    return "Found (Landing page)"

@app.route('/collection/<object_type>/<document_type>/<int:id>')
def view_document(object_type, document_type, id):
    doc = Document.query.filter(Document.object_id == id,
                                Document.type == document_type,
                                PersistentObject.type == object_type).first()

    if not doc:
        return "Not found"

    print doc.enabled

    if not doc.enabled:
        return "Link disabled"

    return redirect(doc.url, code=303)
