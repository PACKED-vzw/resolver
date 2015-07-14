import csv, tempfile
from flask import redirect, request, render_template, flash, make_response
from sqlalchemy.sql import or_
import json
from resolver import app
from resolver.model import Entity, Document, Data, Representation,\
    document_types, data_formats
from resolver.database import db
from resolver.exception import EntityCollisionException,\
    EntityPIDExistsException
from resolver.controllers.user import check_privilege
from resolver.forms import EntityForm
from resolver.util import log
import resolver.kvstore as kvstore

@app.route('/resolver/entity')
@check_privilege
def admin_list_entities(form=None, show_form=None):
    if "application/json" in request.headers["Accept"]:
        return admin_list_entities_dynamic()

    entities = Entity.query.all()
    form = form if form else EntityForm()
    return render_template("resolver/entities.html", title="Entities",
                           entities=entities, form=form,
                           titles_enabled=kvstore.get('titles_enabled'),
                           show_form=show_form)


def admin_list_entities_dynamic():
    entity_link = "<a href=\"/resolver/entity/{0}\">{0}</a>"
    remove_link = "<a class=\"link-delete-entity\" id=\"{0}\"><span class=\"glyphicon glyphicon-remove\"></span></a>"
    log_link = "<a href=\"/resolver/log/id/{0}\"><span class=\"glyphicon glyphicon-time\"></span></a>"

    order_column = int(request.args["order[0][column]"])
    order_dir = request.args["order[0][dir]"]

    if order_column == 0:
        order_column = Entity.type
    elif order_column == 1:
        order_column = Entity.id
    elif order_column == 2:
        order_column = Entity.title
    else:
        return json.dumps({'error': 'Can\'t sort on this column.'})

    order_column = order_column.asc() if order_dir == "asc" else order_column.desc()

    # TODO: search for type too?
    search_str = "%%%s%%" % request.args["search[value]"]
    full_query = Entity.query.filter(or_(Entity.id.like(search_str),
                                         Entity.title.like(search_str)))
    entities = full_query\
        .order_by(order_column)\
        .offset(int(request.args["start"]))\
        .limit(int(request.args["length"])).all()
    data = [[e.type, entity_link.format(e.id), e.title, e.active_documents,
             remove_link.format(e.id), log_link.format(e.id)] for e in entities]

    return json.dumps({'draw': int(request.args["draw"]),
                       'recordsTotal': Entity.query.count(),
                       'recordsFiltered': full_query.count(),
                       'data': data})


@app.route('/resolver/entity', methods=["POST"])
@check_privilege
def admin_new_entity():
    form = EntityForm()
    if form.validate():
        try:
            ent = Entity(type=form.type.data,
                         title=form.title.data,
                         id=form.id.data)
        except EntityPIDExistsException:
            flash("There already exists and entity with this PID.", "warning")
            return admin_list_entities(form=form)
        except EntityCollisionException:
            flash("PID collision detected!", "warning")
            return admin_list_entities(form=form)

        db.session.add(ent)
        db.session.flush()

        db.session.add(Data(ent.id, 'html'))
        db.session.add(Representation(ent.id, 1, reference=True))

        db.session.commit()

        log(ent.id, "Created entity `%s'" % ent)
        return redirect("/resolver/entity/%s" % ent.id)
    else:
        return admin_list_entities(form=form, show_form=True)


@app.route('/resolver/entity/<id>')
@check_privilege
def admin_view_entity(id, form=None):
    ent = Entity.query.filter(Entity.id == id).first()
    if ent:
        form = form if form else EntityForm(obj=ent)
        return render_template("resolver/entity.html", title="Entity",
                               entity=ent, documents=ent.documents, form=form,
                               data_formats=data_formats,
                               titles_enabled=kvstore.get('titles_enabled'))
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

    old = unicode(ent)
    try:
        ent.id = form.id.data
        ent.title = form.title.data
        ent.type = form.type.data
    except EntityCollisionException:
        db.session.rollback()
        flash('There already is an entity in the database using the new PID',
              'warning')
        return admin_view_entity(id, form=form)
    except EntityPIDExistsException:
        db.session.rollback()
        flash("PID collision detected", 'warning')
        return admin_view_entity(id, form=form)

    db.session.commit() #commit changes to DB
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
        log(id, "Removed the entity `%s'" % ent)
        flash("Entity deleted succesfully!", "success")
    return redirect("/resolver/entity")
