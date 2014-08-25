import csv, tempfile
from flask import redirect, request, render_template, flash, make_response
from resolver import app
from resolver.model import Entity, Document, Data, Representation,\
    document_types, data_formats
from resolver.database import db
from resolver.controllers.user import check_privilege
from resolver.forms import EntityForm
from resolver.util import log
import resolver.kvstore as kvstore

@app.route('/resolver/entity')
@check_privilege
def admin_list_entities(form=False):
    entities = Entity.query.all()
    form = form if form else EntityForm()
    return render_template("resolver/entities.html", title="Entities",
                           entities=entities, form=form,
                           title_enabled=kvstore.get('title_enabled'))

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

        db.session.add(Data(ent.id, 'html'))
        db.session.add(Representation(ent.id, 1, reference=True))

        db.session.commit()

        log("added a new entity to the system: %s" % ent)
        # TODO: to flash or not to flash (UX)
        return redirect("/resolver/entity/%s" % ent.id)
    else:
        return admin_list_entities(form=form)

@app.route('/resolver/entity/<id>')
@check_privilege
def admin_view_entity(id, form=None):
    def sort_help(a, b):
        # Helper function for sorting the documents list
        if (type(a)==Data) or (type(b)==Data):
            return 0
        else:
            return -1 if a.order < b.order else 1

    ent = Entity.query.filter(Entity.id == id).first()
    if ent:
        form = form if form else EntityForm(obj=ent)
        documents = sorted(ent.documents, sort_help)
        return render_template("resolver/entity.html", title="Entity",
                               entity=ent, documents=documents, form=form,
                               data_formats=data_formats)
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
    ent.id = form.id.data
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
