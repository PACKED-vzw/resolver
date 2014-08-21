from resolver import app
import resolver.kvstore as kvstore
from resolver.model import Entity, Document, DocumentHit
from resolver.database import db
from resolver.exception import NotFoundException
from flask import redirect, request, render_template

@app.route('/collection/<id>')
@app.route('/collection/<id>/<slug>')
@app.route('/collection/<etype>/id/<id>')
@app.route('/collection/<etype>/id/<id>/<slug>')
def landing_page(id, etype=None, slug=None):
    ent = Entity.query.filter(Entity.id == id).first()

    if not ent:
        return render_template('notice.html', title='Entity Not Found',
                               message='No entity is associated with \'%s\''%id),\
            404

    if etype and etype != ent.type:
        raise NotFoundException()

    if slug:
        if not kvstore.get('title_enabled'):
            raise NotFoundException()
        elif slug != ent.slug:
            raise NotFoundException()

    docs = ent.documents
    docs = filter(lambda doc: doc.enabled, docs)
    return render_template('landing.html',
                           title=ent.title if ent.title else 'Untitled',
                           documents=docs)

@app.route('/collection/<dtype>/<id>')
@app.route('/collection/<dtype>/<id>/<opt1>')
@app.route('/collection/<dtype>/<id>/<opt1>/<opt2>')
def document(id, dtype, opt1=None, opt2=None):
    if dtype == 'representation':
        if opt2:
            return document_representation(id, num=opt1, slug=opt2)
        else:
            return document_representation(id, opt=opt1)
    elif dtype == 'data':
        if opt2:
            return document_data(id, format=opt1, slug=opt2)
        else:
            return document_data(id, opt=opt1)
    else:
        raise NotFoundException()

@app.route('/collection/<etype>/data/<id>')
@app.route('/collection/<etype>/data/<id>/<opt>')
@app.route('/collection/<etype>/data/<id>/<format>/<slug>')
def document_data(id, etype=None, opt=None, format=None, slug=None):
    ent = Entity.query.filter(Entity.id == id).first()
    if not ent:
        raise NotFoundException()

    if opt:
        # opt can be format or slug
        # what if the slug is 'html'?
        return "Skip for now"
    elif format:
        # format also implies slug
        return "Skip for now"
    else:
        # only ID
        doc = Document.query.filter(Document.type == 'data',
                                    Document.entity_id == id).first()
        if not doc:
            raise NotFoundException()

        return show_document(doc)

@app.route('/collection/<etype>/representation/<id>')
@app.route('/collection/<etype>/representation/<id>/<opt>')
@app.route('/collection/<etype>/representation/<id>/<num>/<slug>')
def document_representation(id, etype=None, opt=None, num=None, slug=None):
    ent = Entity.query.filter(Entity.id == id).first()

    if not ent:
        raise NotFoundException()

    if opt:
        # opt can be num or slug
        # how do we differentiate between num and slug?
        # We could try to check if num is parseable as an int, but slug could be
        # parseable as an int also
        return "Skip for now"
    elif num:
        # num also implies slug
        return "Skip for now"
    else:
        # only ID
        doc = Document.query.filter(Document.type == 'representation',
                                    Document.entity_id == id).first()
        if not doc:
            raise NotFoundException()

        return show_document(doc)

def show_document(doc):
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
