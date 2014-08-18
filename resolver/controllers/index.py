from resolver import app
from flask import redirect

@app.route('/')
def index():
    return redirect('/resolver')

@app.route('/resolver')
def admin_index():
    return redirect('/resolver/entity')
