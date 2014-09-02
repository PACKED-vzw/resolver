from flask import make_response
from resolver import app
from resolver.controllers.user import check_privilege
from resolver.model import Log

@app.route('/resolver/log/id/<id>')
@app.route('/resolver/log/limit/<int:limit>')
@check_privilege
def export_log(id=None, limit=None):
    if id:
        logs = Log.query.filter(Log.entity == id).\
               order_by(Log.timestamp.desc()).all()
    else:
        if limit == 0:
            logs = Log.query.order_by(Log.timestamp.desc()).all()
        else:
            logs = Log.query.order_by(Log.timestamp.desc()).limit(limit).all()

    output = ""
    for log in reversed(logs):
        # Newline problems on windows?
        output += str(log) + '\n'

    response = make_response(output)
    response.headers["Content-Disposition"] = 'attachment; filename="log.txt"'
    response.headers["Content-Type"] = 'text/plain'

    return response
