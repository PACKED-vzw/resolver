from flask import redirect, request, render_template, flash, session
from functools import update_wrapper
from resolver import app
from resolver.model import User
from resolver.database import db
from resolver.forms import SigninForm, UserForm
from resolver.util import log

def check_privilege(func):
    """Decorator to provide easy access control to functions."""
    def inner(*args, **kwargs):
        if not session.get('username'):
            # TODO: Save request and replay after user is signed in?
            # TODO: Log unauthorized access?
            flash("You need to be signed in for this action", "warning")
            return redirect("/resolver/signin")
        else:
            return func(*args, **kwargs)
    #func.provide_automatic_options = False
    return update_wrapper(inner, func)

@app.route('/resolver/signin', methods=["POST", "GET"])
def admin_signin():
    form = SigninForm()
    if session.get('username'):
        flash("You are already logged in", "info")
        return redirect('/resolver')
    if form.validate_on_submit():
        user = User.query.filter(User.username ==  form.username.data).first()
        if not user:
            flash("Username incorrect", "danger")
            return render_template('resolver/signin.html', title='Sign in',
                                   form=form)
        if not user.verify_password(form.password.data):
            flash("Password incorrect", "danger")
            return render_template('resolver/signin.html', title='Sign in',
                                       form=form)
        session['username'] = form.username.data
        return redirect('/resolver')
    return render_template('resolver/signin.html', title='Sign in', form=form)

@app.route('/resolver/signout')
@check_privilege
def admin_signout():
    session.pop('username', None)
    return redirect("/resolver/signin")

@app.route('/resolver/user')
@check_privilege
def admin_list_users(form=None):
    users = User.query.all()
    form = form if form else UserForm()
    return render_template("resolver/users.html", title="Users",
                           users=users, form=form)

@app.route('/resolver/user', methods=["POST"])
@check_privilege
def admin_new_user():
    form = UserForm()
    if form.validate():
        user = User.query.filter(User.username == form.username.data).first()
        if user:
            flash("There already is a user named '%s'." % form.username.data,
                  "danger")
            return admin_list_users(form=form)
        # TODO: Do we really need this?
        if form.password.data != form.confirm.data:
            flash("The two passwords do not match.", "warning")
            return admin_list_users(form=form)
        user = User(form.username.data, form.password.data)
        db.session.add(user)
        db.session.commit()
        #log("added user `%s' to the system" % user.username)
        flash("User added succesfully", "success")
        return admin_list_users()
    return admin_list_users(form=form)

@app.route('/resolver/user/delete/<username>')
@check_privilege
def admin_delete_user(username):
    if username == "admin":
        flash("The administrator cannot be removed!", "danger")
        return redirect("/resolver/user")
    if username == session.get('username'):
        flash("You can not remove yourself!", 'warning')
        return redirect("/resolver/user")

    user = User.query.filter(User.username == username).first()
    if not user:
        flash("User not found", "warning")
        return redirect("/resolver/user")
    db.session.delete(user)
    db.session.commit()
    #log("removed user `%s' from the system" % user.username)
    flash("User removed succesfully", "success")
    return redirect("/resolver/user")

@app.route('/resolver/user/<username>')
@check_privilege
def admin_view_user(username):
    form = UserForm()
    user = User.query.filter(User.username == username).first()
    if not user:
        flash("User not found", "warning")
        return redirect("/resolver/user")
    return render_template("resolver/user.html", title="Edit user", user=user, form=form))

@app.route('/resolver/user/<username>', methods=["POST"])
@check_privilege
def admin_change_user_password(username):
    user = User.query.filter(User.username == username).first()
    if not user:
        flash("User not found", "warning")
        return redirect("/resolver/user")
    if request.form['password'] == "":
        flash("Password can not be empty", "warning")
        return render_template("resolver/user.html", title="Edit user",
                               user=user)
    user.change_password(request.form['password'])
    db.session.commit()
    #log("changed the password of user `%s'" % user.username)
    flash("Password changed succesfully", "success")
    return admin_view_user(username)
