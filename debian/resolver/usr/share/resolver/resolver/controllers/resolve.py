from resolver import app
import resolver.kvstore as kvstore
from resolver.model import Entity, Document, DocumentHit, Data, Representation,\
    data_formats
from resolver.database import db
from resolver.exception import NotFoundException
from flask import redirect, request, render_template

DEFAULT_FORMAT = 'html'

@app.route('/collection/<id>')
@app.route('/collection/<id>/<slug>')
@app.route('/collection/<etype>/id/<id>')
@app.route('/collection/<etype>/id/<id>/<slug>')
def landing_page(id, etype=None, slug=None):
    ent = Entity.query.filter(Entity.id == id).first()

    if not ent:
        raise NotFoundException()

    if etype and etype != ent.type:
        raise NotFoundException()

    if slug:
        if not kvstore.get('titles_enabled'):
            raise NotFoundException()
        elif slug != ent.slug:
            raise NotFoundException()

    docs = ent.documents
    #docs = filter(lambda doc: doc.enabled, docs)
    if kvstore.get('titles_enabled'):
        title = ent.title if ent.title else 'Untitled'
    else:
        title = ent.id

    return render_template('landing.html',
                           title=title,
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
    if etype and ent.type != etype:
        raise NotFoundException()

    if opt:
        # opt can be format or slug
        # what if the slug is 'html'?
        # Solution: if opt is in data_formats =>
        #   treat as format, not as slug (even if it is the slug)
        if opt in data_formats:
            doc = Data.query.filter(Document.entity_id == id,
                                    Data.format == opt).first()
        else:
            if kvstore.get('titles_enabled') and\
               ent.slug != opt:
                raise NotFoundException()

            doc = Data.query.filter(Document.entity_id == id,
                                    Data.format == DEFAULT_FORMAT).first()
    elif format:
        # format also implies slug
        if kvstore.get('titles_enabled') and\
           ent.slug != slug:
            raise NotFoundException()

        doc = Data.query.filter(Document.entity_id == id,
                                Data.format == format).first()
    else:
        # only ID
        doc = Data.query.filter(Document.entity_id == id,
                                Data.format == DEFAULT_FORMAT).first()

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
    if etype and ent.type != etype:
        raise NotFoundException()

    if opt:
        # opt can be num or slug
        # how do we differentiate between num and slug?
        # We could try to check if num is parseable as an int, but slug could be
        # parseable as an int also
        # Solution: try to parse as int, if parseable =>
        #   treat it as num, not as slug (even if it is the slug)
        try:
            num = int(opt)
            doc = Representation.query.filter(Representation.order == num,
                                              Document.entity_id == id).first()
        except ValueError:
            # opt == slug
            if kvstore.get('titles_enabled') and\
               ent.slug != opt:
                raise NotFoundException()

            doc = Representation.query.filter(Representation.reference == True,
                                              Document.entity_id == id).first()
    elif num:
        # num also implies slug
        if kvstore.get('titles_enabled') and\
           ent.slug != slug:
            raise NotFoundException()

        doc = Representation.query.filter(Representation.order == num,
                                          Document.entity_id == id).first()
    else:
        # only ID
        doc = Representation.query.filter(Representation.reference == True,
                                          Document.entity_id == id).first()
    if not doc:
        raise NotFoundException()

    return show_document(doc)

def show_document(doc):
    hit = DocumentHit(doc.id, request.remote_addr, request.referrer)
    db.session.add(hit)
    db.session.commit()

    if doc.enabled:
        if doc.url:
            return redirect(doc.url, code=303)
        else:
            title = "No link"
    else:
        title = "Link disabled"

    if doc.notes:
        message = doc.notes
    else:
        message = False

    return render_template("notice.html", title=title, message=message,
                           default_notice=kvstore.get('default_notice_clean'),
                           logo_url=kvstore.get('logo_url'))
