from resolver import app
from resolver.model import PersistentObject, Document,\
    object_types, document_types
from resolver.database import db_session
from resolver.controllers.admin.user import check_privilege
from flask import redirect, request, render_template, flash
from resolver.forms import ObjectForm, DocumentForm
from resolver.util import log

@app.route('/admin/object')
@check_privilege
def admin_list_persistent_objects(form=False):
    objects = PersistentObject.query.all()
    form = form if form else ObjectForm()
    return render_template("admin/objects.html", title="Admin",\
                           objects=objects, form=form)

@app.route('/admin/object', methods=["POST"])
@check_privilege
def admin_new_persistent_object():
    form = ObjectForm()
    if form.validate():
        obj = PersistentObject.query.\
              filter(PersistentObject.id == form.id.data).first()
        if obj:
            flash("ID not unique", "warning")
            return admin_list_persistent_objects(form=form)
        obj = PersistentObject(type=form.type.data,
                               title=form.title.data,
                               id=form.id.data)
        db_session.add(obj)
        db_session.commit()
        log("added a new object to the system: %s" % obj)
        # TODO: to flash or not to flash (UX)
        return redirect("/admin/object/%s" % obj.id)
    else:
        return admin_list_persistent_objects(form=form)

@app.route('/admin/object/<id>')
@check_privilege
def admin_view_persistent_object(id, form=None):
    po = PersistentObject.query.filter(PersistentObject.id == id).first()
    if po:
        documents = po.documents
        form = form if form else DocumentForm()
        return render_template("admin/object.html", title="Admin",
                               object=po, documents=documents, form=form)
    else:
        flash("Object not found!", "danger")
        return redirect("/admin/object")

@app.route('/admin/object/<id>', methods=["POST"])
@check_privilege
def admin_new_document(id):
    form = DocumentForm()
    po = PersistentObject.query.filter(PersistentObject.id == id).first()
    if not po:
        flash("Object for document not found!", "danger")
        return admin_view_persistent_objects()
    if not form.validate():
        return admin_view_persistent_object(id, form=form)
    # TODO: I assume only one instance per document type
    if form.type.data in map(lambda obj: obj.type, po.documents):
        flash("There already is a document of this type", "warning")
        return admin_view_persistent_object(id, form=form)
    document = Document(id, type=form.type.data, url=form.url.data,
                        enabled=form.enabled.data)
    db_session.add(document)
    db_session.commit()
    log("added a new document `%s' to the object `%s'" % (document, po))
    # TODO: to flash or not to flash (UX)
    return redirect('/admin/object/%s' % id)

@app.route('/admin/object/edit/<id>', methods=["GET", "POST"])
@check_privilege
def admin_edit_object(id):
    obj = PersistentObject.query.filter(PersistentObject.id == id).first()

    if not obj:
        flash("Object not found", "warning")
        return redirect("/admin/object")

    if request.method == 'POST':
        form = ObjectForm()

        if not form.validate():
            return render_template("admin/edit_object.html", title="Admin",
                                   object=obj, form=form)
        old = str(obj)
        obj.title = form.title.data
        obj.type = form.type.data
        obj.id = form.id.data
        db_session.commit() #commit changes to DB
        log("changed object `%s' to `%s'" % (old, obj))
        return redirect('/admin/object/%s' % obj.id)
    form = ObjectForm(request.form, obj)
    return render_template("admin/edit_object.html", title="Admin",
                           object=obj, form=form)

#@app.route('/admin/object/<int:id>', methods=["DELETE"])
@app.route('/admin/object/delete/<id>')
@check_privilege
def admin_delete_persistent_object(id):
    po = PersistentObject.query.filter(PersistentObject.id == id).first()
    if not po:
        flash("Object not found!", "danger")
    else:
        db_session.delete(po)
        db_session.commit()
        log("removed the object `%s' from the system" % po)
        flash("Object deleted succesfully!", "success")
    return redirect("/admin/object")

@app.route('/admin/csv', methods=["GET", "POST"])
@check_privilege
def admin_csv_import():
    return "TODO"

@app.route('/admin/export')
@check_privilege
def admin_csv_export():
    data = "'id', 'title', 'object_type', 'document_type', 'url', 'enabled'\n"
    for object in PersistentObject.query.all():
        for document in object.documents:
            data += "'%s', '%s', '%s', '%s', '%s', '%s'\n" %\
                    (object.id, object.title, object.type,
                     document.type, document.url, document.enabled)
    return data
