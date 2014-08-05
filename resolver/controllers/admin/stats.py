from flask import redirect, render_template, flash
from datetime import datetime
from calendar import monthrange
from resolver import app
from resolver.model import PersistentObject, Document, DocumentHit, document_types, object_types
from resolver.controllers.admin.user import check_privilege

@app.route('/admin/stats')
@app.route('/admin/stats/<int:year>/<int:month>')
@check_privilege
def admin_stats_index(year=None, month=None):
    if year == None:
        now = datetime.now()
        year = now.year
        month = now.month
    else:
        # Check if given year and month are sane
        if not (2000 <= year <= 2064):
            flash("Year out of range", "warning")
            return redirect("/admin/stats")

        if not (1 <= month <= 12):
            flash("Month out of range", "warning")
            return redirect("/admin/stats")

    start = datetime(year, month, 1, 0, 0, 0)
    end = datetime(year, month, monthrange(year, month)[1], 23, 59, 59)
    hits_per_document_type = [(type, DocumentHit.query.\
                               filter(DocumentHit.timestamp.between(start, end)).\
                               filter(DocumentHit.document.has(type=type)).\
                               count())
                              for type in document_types]
    hits_per_object_type = [(type, DocumentHit.query.\
                             join(Document).\
                             join(PersistentObject).\
                             filter(DocumentHit.timestamp.between(start, end)).\
                             filter(PersistentObject.type == type).\
                             count())
                            for type in object_types]

    referrers = {}
    for h in DocumentHit.query.filter(DocumentHit.timestamp.between(start, end)):
        referrers[h.referrer] = referrers.get(h.referrer, 0) + 1

    referrers = [t for t in sorted(referrers.iteritems(),
                                   key=lambda (k,v): (v,k),
                                   reverse=True)][0:10]

    return render_template("admin/stats.html", title='Admin',
                           object_hits=hits_per_object_type,
                           document_hits=hits_per_document_type,
                           referrers=referrers)
