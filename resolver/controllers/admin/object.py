from resolver import app
from resolver.model import PersistentObject, Document,\
    object_types, document_types
from resolver.database import db_session
from resolver.controllers.admin.user import check_privilege
from flask import redirect, request, render_template, flash

@app.route('/admin/object')
@check_privilege
def admin_list_persistent_objects():
    objects = PersistentObject.query.all()
    return render_template("admin/objects.html", title="Admin",\
                           objects=objects, types=object_types)

@app.route('/admin/object/<int:id>')
@check_privilege
def admin_view_persistent_object(id):
    po = PersistentObject.query.filter(PersistentObject.id == id).first()

    if po:
        documents = po.documents
        return render_template("admin/object.html", title="Admin",
                               object=po, documents=documents,\
                               types=document_types)
    else:
        flash("Object not found!", "danger")
        return redirect("/admin/object")

#@app.route('/admin/object/<int:id>', methods=["DELETE"])
@app.route('/admin/object/delete/<int:id>')
@check_privilege
def admin_delete_persistent_object(id):
    po = PersistentObject.query.filter(PersistentObject.id == id).first()

    if not po:
        flash("Object not found!", "danger")
    else:

        for doc in po.documents:
            db_session.delete(doc)

        db_session.delete(po)
        db_session.commit()

        flash("Object deleted succesfully!", "success")

    return redirect("/admin/object")

@app.route('/admin/object', methods=["POST"])
@check_privilege
def admin_new_persistent_object():
    if request.form['type'] in object_types:
        obj = PersistentObject(type=request.form['type'],
                               title=request.form['title'])
        db_session.add(obj)
        db_session.commit()
        # TODO: flash or not? (UX)
        return redirect('/admin/object/%s' % obj.id)
    else:
        flash("Type of object not allowed", "danger")
        return admin_view_persistent_objects()

@app.route('/admin/object/edit/<int:id>', methods=["GET", "POST"])
@check_privilege
def admin_edit_object(id):
    obj = PersistentObject.query.filter(PersistentObject.id == id).first()

    if not obj:
        flash("Object not found", "warning")
        return redirect("/admin/object")

    if request.method == 'POST':
        if not(request.form['type'] in object_types):
            flash("Type of object not allowed", "danger")
            render_template("admin/edit_object.html", title="Admin",\
                            object=obj, types=object_types)

        # TODO: Check form (WTForms?)
        obj.title = request.form['title']
        obj.type = request.form['type']
        db_session.commit() #commit changes to DB

        return redirect('/admin/object/%s' % id)

    return render_template("admin/edit_object.html", title="Admin",\
                           object=obj, types=object_types)

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
