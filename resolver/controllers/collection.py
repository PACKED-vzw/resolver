from resolver import app
from resolver.model import PersistentObject, Document, DocumentHit
from resolver.database import db_session
from flask import redirect, request, render_template

@app.route('/collection')
def collection():
    return 'Error: ID required'

@app.route('/collection/<id>')
def view_object(id):
    po = PersistentObject.query.filter(PersistentObject.id == id).first()

    if not po:
        return "Not Found"

    # TODO: Implement default action
    docs = po.documents_by_type
    if docs["data"]:
        return redirect(docs["data"].url, code=303)

    return "Found (Landing page)"

@app.route('/collection/<object_type>/<document_type>/<id>')
@app.route('/collection/<object_type>/<document_type>/<id>/<slug>')
def view_document(object_type, document_type, id, slug=None):
    # TODO: Do we tolerate incorrect slugs? Might cause some problems with SEO?

    doc = Document.query.filter(Document.object_id == id,
                                Document.type == document_type,
                                PersistentObject.type == object_type).first()
    if not doc:
        return "Not found"

    # TODO: make sure we get the right IP address from the WSGI host!!!
    # TODO: is it OK to log a hit, even when the document is disabled?
    hit = DocumentHit(doc.id, request.remote_addr, request.referrer)
    db_session.add(hit)
    db_session.commit()

    if doc.enabled:
        if doc.url:
            return redirect(doc.url, code=303)
        else:
            title = "No link"
            # TODO: Configuration for default messages
            message = "No link is available for this document."
    else:
        title = "Link disabled"
        # TODO: Configuration for default messages
        message = "The link for this document was disabled by an administrator."

    if doc.notes:
        message = doc.notes

    # We return HTTP error code 410 (Gone).
    # TODO: check if this is a good idea (wrt. search engines etc)
    return render_template("notice.html", title=title, message=message), 410
