from resolver import app
from resolver.controllers.admin.user import check_privilege
from flask import redirect

@app.route('/')
def index():
    return redirect('/admin')

@app.route('/admin')
@check_privilege
def admin_index():
    #return render_template("admin/index.html", title="Admin", item="Hello, world!")
    return redirect('/admin/object')
