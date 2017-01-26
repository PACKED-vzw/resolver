from datetime import datetime
from tempfile import NamedTemporaryFile

import cStringIO
from flask import request, render_template, flash, make_response, redirect, session, url_for, abort

from resolver import app
from resolver.controllers.user import check_privilege
from resolver.database import db
from resolver.model import Entity, Data
from resolver.util import UnicodeWriter
from resolver.modules.importer.csv_redis import CSVRedisWrapper, RedisJobMissing
from resolver.modules.importer.legacy import import_file

_csv_header = ['PID', 'entity type', 'title', 'document type', 'URL',
               'enabled', 'notes', 'format', 'reference', 'order']


@app.route('/resolver/csv')
@check_privilege
def admin_csv():
    return render_template('resolver/csv.html', title='Import & Export')


def file_allowed(filename):
    return ('.' in filename) and \
           (filename.rsplit('.', 1)[1].lower() == 'csv')


# TODO: script for imports


@app.route('/resolver/csv/import', methods=["POST"])
@check_privilege
def admin_csv_import():
    # First, we go over the list of all records and gather them in a dictionary, indexed on the PID.
    # Afterwards, for each PID, we check if the PID is already in the database or not
    # - If it isn't: the new entity is created using the data from the first record in the CSV file
    # - If it is (no collision): the entity is updated with the data from the first record in the CSV file
    # - If it is (collision): error!
    # Data documents are updated iff there is a document of the same format
    # Representation documents are updated iff there is a document with the same order

    # TODO: Function too big!

    file = request.files['file']

    if not file:
        flash("No file provided", "warning")
        return redirect("/resolver/csv")

    if not file_allowed(file.filename):
        flash("File not allowed", "warning")
        return redirect("/resolver/csv")

    if app.config['USE_REDIS'] is True:
        csv_wrapper = CSVRedisWrapper()
        csv_wrapper.csv_import(csv_fileobj=file)

        return redirect(url_for('admin_csv_import_status', job_id=csv_wrapper.job.id))

    else:
        import_id, rows, count_pids, failures, bad_records = import_file(file)

        if failures:
            session['bad_records'] = write_bad_records(bad_records)
            flash("There were some errors during import", 'warning')
            return render_template('resolver/csv.html', title='Import & Export',
                                   failures=failures)

        flash('Import successful', 'success')
        return render_template('resolver/csv.html', title="Import & Export",
                               import_log_id=import_id, rows=rows, count_pids=count_pids)


@app.route('/resolver/csv/import/<string:job_id>/status')
@check_privilege
def admin_csv_import_status(job_id):
    csv_wrapper = CSVRedisWrapper()
    try:
        csv_wrapper.get_job(job_id)
    except RedisJobMissing:
        abort(404)
        return ''

    return render_template('resolver/csv_status.html', title='Job {0}: status'.format(job_id), job_id=job_id)


@app.route('/resolver/csv/import/<string:job_id>/finished')
@check_privilege
def admin_csv_import_finished(job_id):
    csv_wrapper = CSVRedisWrapper()
    try:
        csv_wrapper.get_job(job_id)
    except RedisJobMissing:
        abort(404)
        return ''

    failures = csv_wrapper.failures()
    if len(failures) > 0:
        session['bad_records'] = write_bad_records(csv_wrapper.bad_records())
        flash("There were some errors during import", 'warning')
        return render_template('resolver/csv_success.html', title='Job {0}: finished'.format(job_id), job_id=job_id,
                               failures=failures)

    return render_template('resolver/csv_success.html', title='Job {0}: finished'.format(job_id), job_id=job_id)


@app.route('/resolver/csv/import/<string:job_id>/failed')
@check_privilege
def admin_csv_import_failed(job_id):
    csv_wrapper = CSVRedisWrapper()
    try:
        csv_wrapper.get_job(job_id)
    except RedisJobMissing:
        abort(404)
        return ''

    session['bad_records'] = write_bad_records(csv_wrapper.bad_records())

    return render_template('resolver/csv_failure.html', title='Job {0}: failed'.format(job_id), job_id=job_id,
                           failures=csv_wrapper.failures())


def write_bad_records(records):
    file = NamedTemporaryFile(delete=False, suffix='.csv')
    writer = UnicodeWriter(file)
    writer.writerow(_csv_header)
    for record in records:
        writer.writerow(record)
    file.close()
    return file.name


@app.route('/resolver/csv/records')
def get_bad_records():
    if not session.get('bad_records'):
        flash("File not found", 'warning')
        return redirect("/resolver/csv")
    file = open(session.get('bad_records'))
    filename = "badrecords_%s" % datetime.now().strftime('%d%m%Y_%H%M%S')
    response = make_response(file.read())
    response.headers["Content-Disposition"] = 'attachment; filename="%s.csv"' % filename
    response.headers["Content-Type"] = 'text/csv'
    file.close()
    return response


@app.route('/resolver/csv/export')
@check_privilege
def admin_csv_export():
    # TODO: Fix all the 'None' in export
    entities = Entity.query.all()
    file = cStringIO.StringIO()
    writer = UnicodeWriter(file)
    writer.writerow(_csv_header)
    # TODO add column persistent_link (as separate export?)
    # TODO ignore column persistent_link while importing (but column is not required)
    for entity in entities:
        for document in entity.documents:
            if type(document) == Data:
                writer.writerow([entity.id, entity.type, entity.title, 'data',
                                 unicode(document.url) if document.url else '',
                                 '1' if document.enabled else '0',
                                 unicode(document.notes) if document.notes else '',
                                 document.format, '', ''])
            else:
                writer.writerow([entity.id, entity.type, entity.title,
                                 'representation',
                                 unicode(document.url) if document.url else '',
                                 '1' if document.enabled else '0',
                                 unicode(document.notes) if document.notes else '',
                                 '',
                                 '1' if document.reference else '0',
                                 unicode(document.order)])

    file.seek(0)
    filename = "export_%s.csv" % datetime.now().strftime('%d%m%Y_%H%M%S')
    response = make_response(file.read())
    response.headers["Content-Disposition"] = 'attachment; filename="%s.csv"' % filename
    response.headers["Content-Type"] = 'text/csv'
    file.close()
    return response


@app.route('/resolver/csv/purge')
@check_privilege
def purge_database():
    Entity.query.delete()
    db.session.commit()
    flash("Database has been purged", "success")
    return redirect('/resolver/csv')
