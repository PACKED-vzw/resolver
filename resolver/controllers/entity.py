import csv, tempfile
from flask import redirect, request, render_template, flash, make_response
from resolver import app
from resolver.model import Entity, Document, document_types, cleanID
from resolver.database import db
from resolver.controllers.user import check_privilege
from resolver.forms import EntityForm
from resolver.util import log

@app.route('/resolver/entity')
@check_privilege
def admin_list_entities(form=False):
    entities = Entity.query.all()
    form = form if form else EntityForm()
    return render_template("resolver/entities.html", title="Entities",\
                           entities=entities, form=form)

@app.route('/resolver/entity', methods=["POST"])
@check_privilege
def admin_new_entity():
    form = EntityForm()
    if form.validate():
        ent = Entity.query.\
              filter(Entity.id == form.id.data).first()
        if ent:
            flash("ID not unique", "warning")
            return admin_list_entities(form=form)
        ent = Entity(type=form.type.data,
                     title=form.title.data,
                     id=form.id.data)
        db.session.add(ent)
        db.session.flush()

        for type in document_types:
            db.session.add(Document(ent.id, type))

        db.session.commit()

        log("added a new entity to the system: %s" % ent)
        # TODO: to flash or not to flash (UX)
        return redirect("/resolver/entity/%s" % ent.id)
    else:
        return admin_list_entities(form=form)

@app.route('/resolver/entity/<id>')
@check_privilege
def admin_view_entity(id, form=None):
    ent = Entity.query.filter(Entity.id == id).first()
    if ent:
        form = form if form else EntityForm(obj=ent)
        documents = ent.documents
        return render_template("resolver/entity.html", title="Entity",
                               entity=ent, documents=documents, form=form)
    else:
        flash("Entity not found!", "danger")
        return redirect("/resolver/entity")

@app.route('/resolver/entity/edit/<id>', methods=["POST"])
@check_privilege
def admin_edit_entity(id):
    ent = Entity.query.filter(Entity.id == id).first()

    if not ent:
        flash("Entity not found", "warning")
        return redirect("/resolver/entity")

    form = EntityForm()

    if not form.validate():
        return admin_view_entity(id, form=form)

    old = str(ent)
    ent.title = form.title.data
    ent.type = form.type.data
    ent.id = cleanID(form.id.data)
    db.session.commit() #commit changes to DB
    log("changed entity `%s' to `%s'" % (old, ent))
    return redirect('/resolver/entity/%s' % ent.id)

@app.route('/resolver/entity/delete/<id>')
@check_privilege
def admin_delete_entity(id):
    ent = Entity.query.filter(Entity.id == id).first()
    if not ent:
        flash("Entity not found!", "danger")
    else:
        db.session.delete(ent)
        db.session.commit()
        log("removed the entity `%s' from the system" % ent)
        flash("Entity deleted succesfully!", "success")
    return redirect("/resolver/entity")
