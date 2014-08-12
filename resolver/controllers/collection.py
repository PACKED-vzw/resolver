from resolver import app
from resolver.model import PersistentObject, Document, DocumentHit
from resolver.database import db
from resolver.exception import NotFoundException
from resolver.matcher import matcher
from flask import redirect, request, render_template

@app.route('/<path:path>')
def catch_all(path):
    return handler(**matcher.match(path))

def handler(id=None, slug=None, otype=None, dtype=None):
    po = PersistentObject.query.filter(PersistentObject.id == id).first()

    if not po:
        return render_template('notice.html', title='Object Not Found',
                               message='No object is associated with \'%s\''%id),\
            404

    if not dtype:
        # TODO: Default redirect instead of landing page?
        # TODO: List both enabled and disabled links, or only enabled ones?
        docs = po.documents
        docs = filter(lambda doc: doc.enabled, docs)
        return render_template('landing.html',
                               title=po.title if po.title else 'Untitled',
                               documents=docs)
    else:
        # having dtype implies having otype
        # TODO: complain about wrong object type or not?
        if not otype == po.type:
            return render_template('notice.html', title='Wrong object type',
                                   message="Wrong object type provided")
        # TODO: complain about wrong slug or not?
        if slug and not slug == po.slug:
            raise NotFoundException()

        doc = Document.query.filter(Document.object_id == id,
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
