from flask import redirect, request, render_template, flash, session, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from functools import update_wrapper
from resolver import app, lm
from resolver.model import User
from resolver.database import db
from resolver.forms import SigninForm, UserForm, ResetForm
from resolver.util import log


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@lm.token_loader
def load_token(token):
    return User.query.filter(User.auth_token == str(token)).first()


@app.before_request
def before_request():
    g.user = current_user


def check_privilege(func):
    """Decorator to provide easy access control to functions."""

    def inner(*args, **kwargs):
        if current_user.is_authenticated:
            return func(*args, **kwargs)
        else:
            return redirect("/resolver/signin")

    # func.provide_automatic_options = False
    return update_wrapper(inner, func)


def is_admin():
    """
    Function to check whether the current user is the administrator
    :return bool:
    """
    if current_user.is_admin:
        return True
    else:
        flash("You do not have sufficient rights to modify or create users.", "danger")
        return False


@app.route('/resolver/signin', methods=["POST", "GET"])
def admin_signin():
    if g.user is not None and g.user.is_authenticated:
        return redirect('/resolver')
    form = SigninForm()
    if form.validate_on_submit():
        user = User.query.filter(User.username == form.username.data).first()
        if not user:
            flash('Incorrect username and/or password.', "danger")
            return render_template('resolver/signin.html', title='Sign in',
                                   form=form)
        if user.verify_password(form.password.data):
            login_user(user)
            return redirect('/resolver')
        flash('Incorrect username and/or password.', "danger")
        return render_template('resolver/signin.html', title='Sign in',
                               form=form)
    return render_template('resolver/signin.html', title='Sign in', form=form)


@app.route('/resolver/signout')
@login_required
def admin_signout():
    logout_user()
    return redirect("/resolver/signin")


@app.route('/resolver/user')
@login_required
def admin_list_users(form=None):
    users = User.query.all()
    form = form if form else UserForm()
    return render_template("resolver/users.html", title="Users",
                           users=users, form=form)


@app.route('/resolver/user', methods=["POST"])
@login_required
def admin_new_user():
    if not is_admin():
        return admin_list_users()
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
        # log("added user `%s' to the system" % user.username)
        flash("User added succesfully", "success")
        return admin_list_users()
    return admin_list_users(form=form)


@app.route('/resolver/user/delete/<username>')
@login_required
def admin_delete_user(username):
    if not is_admin():
        return redirect("/resolver/user")
    if username == "admin":
        flash("The administrator cannot be removed!", "danger")
        return redirect("/resolver/user")
    user = User.query.filter(User.username == username).first()
    if not user:
        flash("User not found", "warning")
        return redirect("/resolver/user")
    db.session.delete(user)
    db.session.commit()
    # log("removed user `%s' from the system" % user.username)
    flash("User removed succesfully", "success")
    return redirect("/resolver/user")


@app.route('/resolver/user/<username>')
@login_required
def admin_view_user(username):
    if current_user.username != username and not is_admin():
        return redirect("/resolver/user")
    form = ResetForm()
    user = User.query.filter(User.username == username).first()
    if not user:
        flash("User not found", "warning")
        return redirect("/resolver/user")
    return render_template("resolver/user.html", title="Edit user", user=user, form=form)


@app.route('/resolver/user/<username>', methods=["POST"])
@login_required
def admin_change_user_password(username):
    if current_user.username != username and not is_admin():
        return redirect("/resolver/user")
    form = ResetForm()
    user = User.query.filter(User.username == username).first()
    if form.validate():
        if not user:
            flash("User not found", "warning")
            return redirect("/resolver/user")
        # TODO: Do we really need this?
        if form.password.data != form.confirm.data:
            flash("The two passwords do not match.", "warning")
            return redirect("/resolver/user/%s" % username)
        user.change_password(form.password.data)
        db.session.commit()
        # log("changed the password of user `%s'" % user.username)
        flash("Password changed succesfully", "success")
    return render_template("resolver/user.html", title="Edit user", user=user, form=form)
