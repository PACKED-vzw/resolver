from resolver import app
from resolver.model import PersistentObject, Document, User,\
    object_types, document_types
from resolver.database import db_session
from flask import redirect, request, render_template, flash, session

from functools import update_wrapper

# TODO: Edit titles everywhere
# TODO: File is getting too large, refactor to smaller files

def check_privilege(func):
    """Decorator to provide easy access control to functions."""
    def inner(*args, **kwargs):
        if not session.get('username'):
            # TODO: Save request and replay after user is signed in?
            flash("You need to be signed in for this action", "warning")
            return redirect("/admin/signin")
        else:
            return func(*args, **kwargs)

    #func.provide_automatic_options = False
    return update_wrapper(inner, func)

@app.route('/admin/signin', methods=["POST", "GET"])
def admin_signin():
    # TODO: Check if already signed in
    if request.method == "POST":
        # TODO: form validation
        user = User.query.filter(User.username ==  request.form['username']).first()

        if not user:
            flash("Username incorrect", "danger")
            return render_template('admin/signin.html', title='Admin')

        if not user.verify_password(request.form['password']):
            flash("Password incorrect", "danger")
            return render_template('admin/signin.html', title='Admin')

        session['username'] = request.form['username']

        flash("Success!", "success")
        return redirect('/admin')

    return render_template('admin/signin.html', title='Admin')

@app.route('/admin/signout')
@check_privilege
def admin_signout():
    session.pop('username', None)
    flash("Goodbye", "success")
    return redirect("/admin/signin")

@app.route('/')
def index():
    return redirect('/admin')

@app.route('/admin')
@check_privilege
def admin_index():
    #return render_template("admin/index.html", title="Admin", item="Hello, world!")
    return redirect('/admin/object')

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

@app.route('/admin/document/<int:id>')
@check_privilege
def admin_view_document(id):
    doc = Document.query.filter(Document.id == id).first()
    po = doc.persistent_object

    if not doc:
        flash("Document not found", "warning")
        return redirect("/admin/object")

    return render_template("admin/document.html", title="Admin",\
                           document=doc, po=po)

#@app.route('/admin/document/<int:id>', methods=["DELETE"])
@app.route('/admin/document/delete/<int:id>')
@check_privilege
def admin_delete_document(id):
    doc = Document.query.filter(Document.id == id).first()

    if not doc:
        flash("Document not found", "warning")
        return redirect("/admin/object")

    object_id = doc.object_id

    db_session.delete(doc)
    db_session.commit()

    flash("Document deleted succesfully", "success")

    return redirect("/admin/object/%s" % object_id)

@app.route('/admin/document/<int:id>', methods=["POST"])
@check_privilege
def admin_new_document(id):
    po = PersistentObject.query.filter(PersistentObject.id == id).first()

    if not po:
        flash("Object for document not found!", "danger")
        return admin_view_persistent_objects()

    if not(request.form['type'] in document_types):
        flash("Type of document not allowed", "danger")
        return admin_view_persistent_object(id)

    # TODO: I assume only one instance per document type
    if request.form['type'] in map(lambda obj: obj.type, po.documents):
        flash("There already is a document of this type", "warning")
        return admin_view_persistent_object(id)

    # TODO: Check if URL is not empty and sane (WTForms?)
    document = Document(id, type=request.form['type'], url=request.form['url'])
    db_session.add(document)
    db_session.commit()

    # TODO: to flash or not to flash (UX)

    return redirect('/admin/object/%s' % id)

@app.route('/admin/document/edit/<int:id>', methods=["GET", "POST"])
@check_privilege
def admin_edit_document(id):
    doc = Document.query.filter(Document.id == id).first()

    if not doc:
        flash("Document not found", "warning")
        return redirect("/admin/object")

    if request.method == 'POST':
        if not(request.form['type'] in document_types):
            flash("Type of document not allowed", "danger")
            #return admin_view_persistent_object(id)
            return render_template("admin/edit_document.html", title="Admin",\
                                   document=doc, types=document_types)

        # TODO: I assume only one instance per document type
        if (request.form['type'] != doc.type) and\
           (request.form['type'] in map(lambda obj: obj.type,\
                                        doc.persistent_object.documents)):
            flash("There already is a document of this type", "warning")
            return render_template("admin/edit_document.html", title="Admin",\
                                   document=doc, types=document_types)

        # TODO: Check form (WTForms?)
        doc.enabled = 'enabled' in request.form
        doc.type = request.form['type']
        doc.url = request.form['url']
        db_session.commit() #commit changes to DB

        return redirect('/admin/document/%s' % id)

    return render_template("admin/edit_document.html", title="Admin",\
                           document=doc, types=document_types)

@app.route('/admin/user')
@check_privilege
def admin_list_users():
    users = User.query.all()
    return render_template("admin/users.html", title="Admin", users=users)

@app.route('/admin/user', methods=["POST"])
@check_privilege
def admin_new_user():
    # TODO: form validation
    user = User.query.filter(User.username == request.form['username']).first()

    if user:
        flash("There already is a user named '%s'." % request.form['username'],\
              "danger")
        return admin_list_users()

    user = User(request.form['username'], request.form['password'])

    db_session.add(user)
    db_session.commit()

    flash("User added succesfully", "success")
    return admin_list_users()

@app.route('/admin/user/delete/<username>')
@check_privilege
def admin_delete_user(username):
    if username == "admin":
        flash("The administrator cannot be removed!", "danger")
        return redirect("/admin/user")

    user = User.query.filter(User.username == username).first()

    if not user:
        flash("User not found", "warning")
        return redirect("/admin/user")

    db_session.delete(user)
    db_session.commit()

    flash("User removed succesfully", "success")

    return redirect("/admin/user")

@app.route('/admin/user/<username>')
@check_privilege
def admin_view_user(username):
    user = User.query.filter(User.username == username).first()

    if not user:
        flash("User not found", "warning")
        return redirect("/admin/user")

    return render_template("admin/user.html", title="Admin", user=user)

@app.route('/admin/user/<username>', methods=["POST"])
@check_privilege
def admin_change_user_password(username):
    user = User.query.filter(User.username == username).first()

    if not user:
        flash("User not found", "warning")
        return redirect("/admin/user")

    user.change_password(request.form['password'])
    db_session.commit()

    flash("Password changed succesfully", "success")
    return admin_view_user(username)

@app.route('/admin/csv', methods=["GET", "POST"])
@check_privilege
def admin_csv_import():
    return "TODO"
