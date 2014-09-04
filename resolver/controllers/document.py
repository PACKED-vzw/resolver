import json
from resolver import app
from resolver.util import log
from resolver.model import Entity, Document, Data, Representation,\
    entity_types, document_types, data_formats
from resolver.forms import DataForm, RepresentationForm
from resolver.database import db
from resolver.controllers.user import check_privilege
from flask import redirect, request, render_template, flash

@app.route('/resolver/document/<int:id>.json')
@check_privilege
def admin_view_document_json(id):
    doc = Document.query.filter(Document.id == id).first()

    if not doc:
        return json.dumps({'errors':[{'detail':'Document ID invalid'}]})

    return json.dumps(doc.to_dict())

@app.route('/resolver/document/delete/<int:id>')
@check_privilege
def admin_delete_document(id):
    doc = Document.query.filter(Document.id == id).first()
    entity_id = doc.entity_id
    if not doc:
        flash("Document not found", "warning")
        return redirect("/resolver/entity")

    if type(doc) == Representation:
        if doc.reference:
            count = Representation.query.\
                    filter(Document.entity_id == entity_id).count()
            if count > 1:
                flash("Please select another representation to be reference first",
                      'warning')
                return redirect("/resolver/entity/%s" % entity_id)

        db.session.delete(doc)
        db.session.flush()

        i = 1
        reps = Representation.query.\
               filter(Document.entity_id == entity_id).\
               order_by(Representation.order.asc()).all()
        for rep in reps:
            rep.order = i
            i += 1
    else:
        db.session.delete(doc)

    log(entity_id, "Removed the document `%s'" %
        (doc, doc.entity))
    db.session.commit()
    flash("Document deleted succesfully", "success")
    return redirect("/resolver/entity/%s" % entity_id)

@app.route('/resolver/document/representation/up/<int:id>')
@check_privilege
def admin_representation_up(id):
    doc = Document.query.filter(Document.id == id).first()
    if (not doc) or (doc.type != 'representation'):
        flash('Document not found or wrong type', 'danger')
        return redirect("/resolver/entity/%s" % doc.entity_id)\
            if doc else redirect("/resolver/entity")

    if doc.order != 1:
        up = Representation.query.filter(Document.entity_id == doc.entity_id,
                                         Representation.order == (doc.order-1)).\
            first()
        if up:
            doc.order = doc.order - 1
            up.order = up.order + 1
            db.session.commit()
            log(doc.entity_id, "Moved document `%s' up one position" % doc)

    return redirect("/resolver/entity/%s" % doc.entity_id)

@app.route('/resolver/document/representation/down/<int:id>')
@check_privilege
def admin_representation_down(id):
    doc = Document.query.filter(Document.id == id).first()
    if (not doc) or (doc.type != 'representation'):
        flash('Document not found or wrong type', 'danger')
        return redirect("/resolver/entity/%s" % doc.entity_id)\
            if doc else redirect("/resolver/entity")

    next = Representation.query.filter(Document.entity_id == doc.entity_id,
                                       Representation.order == (doc.order + 1)).\
        first()
    if next:
        doc.order = doc.order + 1
        next.order = next.order - 1
        db.session.commit()
        log(doc.entity_id, "Moved document `%s' down one position" % doc)

    return redirect("/resolver/entity/%s" % doc.entity_id)

@app.route('/resolver/document/data/<entity_id>', methods=["POST"])
@check_privilege
def admin_add_data_json(entity_id):
    ent = Entity.query.filter(Entity.id == entity_id).first()
    if not ent:
        return json.dumps({'errors':[{'detail':'Entity not found'}]})

    form = DataForm()

    if not form.validate():
        return form_errors_json(form)

    docs = Data.query.filter(Document.entity_id == ent.id,
                             Data.format == form.format.data).all()
    if len(docs) != 0:
        return json.dumps({'errors':[{'title':'Wrong format',
                                      'detail':'Duplicate format'}]})

    doc = Data(ent.id, form.format.data, url=form.url.data,
               enabled=form.enabled.data, notes=form.notes.data)
    log(doc.entity_id, "Added data document `%s'" % doc)
    db.session.add(doc)
    db.session.commit()

    return json.dumps({'success':True})

@app.route('/resolver/document/representation/<entity_id>', methods=["POST"])
@check_privilege
def admin_add_representation_json(entity_id):
    ent = Entity.query.filter(Entity.id == entity_id).first()
    if not ent:
        return json.dumps({'errors':[{'detail':'Entity not found'}]})

    form = RepresentationForm()

    if not form.validate():
        return form_errors_json(form)

    ref = Representation.query.filter(Document.entity_id == ent.id,
                                      Representation.reference == True).first()
    if form.reference.data:
        if ref:
            ref.reference = False
    elif not ref:
        return json.dumps({'errors':[{'title':'Reference error',
                                      'detail':'At least one representation has to be the reference image.'}]})

    highest = Representation.query.\
              filter(Document.entity_id == ent.id).\
              order_by(Representation.order.desc()).first()
    if highest:
        order = highest.order + 1
    else:
        order = 1

    rep = Representation(ent.id, order, url=form.url.data, label=form.label.data,
                         enabled=form.enabled.data, notes=form.notes.data,
                         reference=form.reference.data)
    log(doc.entity_id, "Added representation document `%s'" % doc)
    db.session.add(rep)
    db.session.commit()

    return json.dumps({'success':True})

@app.route('/resolver/document/edit/<int:id>.json', methods=["POST"])
@check_privilege
def admin_edit_document_json(id):
    doc = Document.query.filter(Document.id == id).first()

    if not doc:
        return json.dumps({'errors':[{'detail':'Document not found'}]})

    # We can still parse the form from the request data
    if type(doc) == Data:
        form = DataForm()
    else:
        form = RepresentationForm()

    if form.validate():
        old = unicode(doc)

        doc.enabled = form.enabled.data
        doc.url = form.url.data
        doc.notes = form.notes.data

        if doc.type == 'data':
            docs = Data.query.filter(Document.entity_id == doc.entity_id,
                                     Data.format == form.format.data,
                                     Document.id != doc.id).all()
            if len(docs) != 0:
                db.session.rollback()
                return json.dumps({'errors':[{'title':'Wrong format',
                                              'detail':'Duplicate format'}]})

            doc.format = form.format.data
        else:
            # Representation
            doc.label = form.label.data

            # Reference bookkeeping
            ref = Representation.query.\
                  filter(Document.entity_id == doc.entity_id,
                         Document.id != doc.id,
                         Representation.reference == True).first()
            if form.reference.data:
                if ref:
                    ref.reference = False

                doc.reference = True
            elif not ref:
                db.session.rollback()
                return json.dumps({'errors':[{'title':'Reference error',
                                              'detail':'At least one representation has to be the reference image.'}]})

        db.session.commit() #commit changes to DB
        return json.dumps({'success':True})
    else:
        return form_errors_json(form)

def form_errors_json(form):
    errors = []
    for t, msgs in form.errors.iteritems():
        for msg in msgs:
            errors.append({'title':t, 'detail':msg})

    return json.dumps({'errors':errors})
