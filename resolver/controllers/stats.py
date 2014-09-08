from flask import redirect, render_template, flash
from datetime import datetime
from calendar import monthrange
from resolver import app
from resolver.database import db
from resolver.model import Entity, Document, DocumentHit, document_types,\
    entity_types
from resolver.controllers.user import check_privilege

@app.route('/resolver/stats')
@app.route('/resolver/stats/<int:year>/<int:month>')
@check_privilege
def admin_stats_index(year=None, month=None):
    # TODO: Support for year and month

    # Q: Is this horrible code?
    # A: Yes. Yes it is.

    now = datetime.now()
    year = now.year
    month = now.month
    start = datetime(year, month, 1, 0, 0, 0)
    end = datetime(year, month, monthrange(year, month)[1], 23, 59, 59)


    entities = db.session.\
               query(Entity.type,
                     db.func.count(Entity.id).label('total')).\
               group_by(Entity.type).\
               all()
    total = reduce(lambda sum,c: sum+c[1], entities, 0)

    work_total = [t[1] for t in entities if t[0] == 'work']
    work_total = work_total[0] if work_total else 0

    agent_total = [t[1] for t in entities if t[0] == 'agent']
    agent_total = agent_total[0] if agent_total else 0

    concept_total = [t[1] for t in entities if t[0] == 'concept']
    concept_total = concept_total[0] if concept_total else 0

    event_total = [t[1] for t in entities if t[0] == 'event']
    event_total = event_total[0] if event_total else 0

    docs = Document.query
    docs_active = docs.filter(Document.enabled == True,
                              Document.url != '',
                              Document.url != 'None')

    docs_count =  docs.count()
    docs_active_count = docs_active.count()

    data_count = docs.filter(Document.type == 'data').count()
    data_active_count = docs_active.filter(Document.type == 'data').count()

    repr_count = docs_count - data_count
    repr_active_count = docs_active_count - data_active_count


    total_hits = db.session.\
                 query(db.func.count(DocumentHit.id)).\
                 filter(DocumentHit.timestamp.between(start, end)).\
                 first()

    work_hits = db.session.\
                query(db.func.count(DocumentHit.id)).\
                join(Document).\
                join(Entity).\
                filter(DocumentHit.timestamp.between(start, end)).\
                filter(Entity.type == 'work').\
                first()[0]
    agent_hits = db.session.\
                 query(db.func.count(DocumentHit.id)).\
                 join(Document).\
                 join(Entity).\
                 filter(DocumentHit.timestamp.between(start, end)).\
                 filter(Entity.type == 'agent').\
                 first()[0]
    concept_hits = db.session.\
                   query(db.func.count(DocumentHit.id)).\
                   join(Document).\
                   join(Entity).\
                   filter(DocumentHit.timestamp.between(start, end)).\
                   filter(Entity.type == 'concept').\
                   first()[0]
    event_hits = db.session.\
                 query(db.func.count(DocumentHit.id)).\
                 join(Document).\
                 join(Entity).\
                 filter(DocumentHit.timestamp.between(start, end)).\
                 filter(Entity.type == 'event').\
                 first()[0]

    data_hits = db.session.\
                query(db.func.count(DocumentHit.id)).\
                join(Document).\
                filter(DocumentHit.timestamp.between(start, end)).\
                filter(Document.type == 'data').\
                first()[0]
    repr_hits = db.session.\
                query(db.func.count(DocumentHit.id)).\
                join(Document).\
                filter(DocumentHit.timestamp.between(start, end)).\
                filter(Document.type == 'representation').\
                first()[0]

    top10_ref = db.session.\
                query(db.func.count(DocumentHit.referrer).label('total'),
                      DocumentHit.referrer).\
                filter(DocumentHit.timestamp.between(start, end)).\
                group_by(DocumentHit.referrer).\
                order_by('total DESC').\
                limit(10).\
                all()
    top10_ents = db.session.\
                 query(db.func.count(DocumentHit.id).label('total'),
                       Entity.id).\
                 join(Document).\
                 join(Entity).\
                 filter(DocumentHit.timestamp.between(start, end)).\
                 group_by(Entity.id).\
                 order_by('total DESC').\
                 limit(10).\
                 all()

    return render_template('resolver/stats.html', title='Statistics',
                           entities_num_work=work_total,
                           entities_num_agent=agent_total,
                           entities_num_concept=concept_total,
                           entities_num_event=event_total,
                           entities_total=total,
                           work_hits=work_hits,
                           agent_hits=agent_hits,
                           concept_hits=concept_hits,
                           event_hits=event_hits,
                           total_hits=total_hits[0],
                           data_total=data_count,
                           data_active=data_active_count,
                           data_hits=data_hits,
                           repr_total=repr_count,
                           repr_active=repr_active_count,
                           repr_hits=repr_hits,
                           docs_total=docs_count,
                           docs_active=docs_active_count,
                           referrers=top10_ref,
                           top10_ents=top10_ents)
