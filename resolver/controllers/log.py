from flask import make_response
from resolver import app
from resolver.controllers.user import check_privilege
from resolver.model import Log, ImportLog


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
        output += unicode(log) + '\n'

    response = make_response(output)
    response.headers["Content-Disposition"] = 'attachment; filename="log.txt"'
    response.headers["Content-Type"] = 'text/plain'

    return response


@app.route ('/resolver/log/import/<id>')
@check_privilege
def export_import_log (id):
    logs = ImportLog.query.filter(ImportLog.import_id == id).order_by(ImportLog.timestamp.desc()).all()
    output = ""
    for log in logs:
        output += unicode (log) + '\n'

    response = make_response (output)
    response.headers["Content-Disposition"] = 'attachment; filename="import_log' + str (id) + '.txt"'
    response.headers["Content-Type"] = 'text/plain'

    return response