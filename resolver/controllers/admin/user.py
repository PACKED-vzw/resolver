from resolver import app
from resolver.model import User
from resolver.database import db_session
from flask import redirect, request, render_template, flash, session
from functools import update_wrapper

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
