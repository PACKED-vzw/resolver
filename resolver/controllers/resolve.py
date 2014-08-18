from resolver import app
from resolver.model import Entity, Document, DocumentHit
from resolver.database import db
from resolver.exception import NotFoundException
from resolver.matcher import matcher
from flask import redirect, request, render_template

@app.route('/<path:path>')
def catch_all(path):
    return handler(**matcher.match(path))

def handler(id=None, slug=None, etype=None, dtype=None):
    ent = Entity.query.filter(Entity.id == id).first()

    if not ent:
        return render_template('notice.html', title='Entity Not Found',
                               message='No entity is associated with \'%s\''%id),\
            404

    # TODO: Complain about wrong slug?
    if slug and slug != ent.slug:
        raise NotFoundException()

    # TODO: Complain about wrong entity type?
    if etype and etype != ent.type:
        raise NotFoundException()

    if not dtype:
        # TODO: Default redirect instead of landing page?
        # TODO: List both enabled and disabled links, or only enabled ones?
        docs = ent.documents
        docs = filter(lambda doc: doc.enabled, docs)
        return render_template('landing.html',
                               title=ent.title if ent.title else 'Untitled',
                               documents=docs)
    else:
        doc = Document.query.filter(Document.entity_id == id,
                                    Document.type == dtype).first()
        if not doc:
            raise NotFoundException()

        # TODO: is it OK to log a hit, even when the document is disabled?
        hit = DocumentHit(doc.id, request.remote_addr, request.referrer)
        db.session.add(hit)
        db.session.commit()

        if doc.enabled:
            if doc.url:
                return redirect(doc.url, code=303)
            else:
                title = "No link"
                # TODO: Configuration for default messages
                message = "No link is available for this entity."
        else:
            title = "Link disabled"
            # TODO: Configuration for default messages
            message = "The link for this document was disabled by an administrator."

        if doc.notes:
            message = doc.notes

        # We return HTTP error code 410 (Gone).
        # TODO: check if this is a good idea (wrt. search engines etc)
        return render_template("notice.html", title=title, message=message), 410
