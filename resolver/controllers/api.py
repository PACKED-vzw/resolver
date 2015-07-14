from flask import redirect, request, render_template, flash, session
from functools import update_wrapper
import json
from jsonschema import validate, ValidationError
import operator
from resolver import app
from resolver.exception import *
from resolver.model import *
from resolver.database import db
from resolver.forms import SigninForm, EntityForm
from resolver.util import log
from resolver import csrf


# TODO: Logging


entity_schema = {
    "properties": {
        "domain": {"type": "string"},
        "type": {"type": "string",
                 "enum": ["work", "concept", "event", "agent"]},
        "id": {"type": "string"},
        "title": {"type": "string"},
        "documents": {"type": "array",
                      "items": {"type": "integer"}},
        "persistentURIs": {"type": "array",
                           "items": {"type": "string"}}
    },
    "required": ["type", "id"]
}


document_schema = {
    "oneOf": [
        {"$ref": "#/definitions/data"},
        {"$ref": "#/definitions/representation"}
    ],
    "definitions": {
        "document": {
            "properties": {
                "id": {"type": "integer"},
                "entity": {"type": "string"},
                "enabled": {"type": "boolean"},
                "notes": {"type": "string"},
                "url": {"type": "string"},
                "type": {"type": "string",
                         "enum": ["data", "representation"]},
                "resolves": {"type": "boolean"}
            },
            "required": ["entity", "enabled", "type"]
        },
        "data": {
            "allOf": [
                {"$ref": "#/definitions/document"},
                {"properties":
                    {"format": {"type": "string",
                                "enum": ["html", "json", "pdf", "xml"]},
                     "type": {"type": "string", "enum": ["data"]}},
                 "required": ["format"]}]
        },
        "representation": {
            "allOf": [
                {"$ref": "#/definitions/document"},
                {"properties":
                     {"order": {"type": "integer"},
                      "reference": {"type": "boolean"},
                      "label": {"type": "string"},
                      "type": {"type": "string", "enum": ["representation"]}},
                 "required": ["reference"]}]
        }
    }
}


def check_privilege(func):
    """Decorator to provide easy access control to functions."""
    def inner(*args, **kwargs):
        if not session.get('username'):
            return '{"errors":[{"title": "Authentication required"}]}', 403
        else:
            return func(*args, **kwargs)

    return update_wrapper(inner, func)


@csrf.exempt
@app.route("/api/login", methods=["POST"])
def login():
    # TODO: rate limiting

    if session.get('username'):
        raise Exception("TODO")
    form = SigninForm(csrf_enabled=False)
    if form.validate_on_submit():
        user = User.query.filter(User.username == form.username.data).first()
        if not user:
            return '{"errors":[{"title": "Username not found"}]}', 403
        if not user.verify_password(form.password.data):
            return '{"errors":[{"title": "Wrong password"}]}', 403
        session['username'] = user.username
        return "", 204
    errors = [{'title': 'Malformed parameter',
               'detail': 'Field %s: %s' % (field, ' '.join(error))}
              for field, error in form.errors.iteritems()]
    return json.dumps({'errors': errors}), 403


@app.route("/api/logout")
@check_privilege
def logout():
    session.pop('username', None)
    return "", 204


@csrf.exempt
@app.route("/api/entity", methods=["GET"])
@check_privilege
def get_entities():
    entities = db.session.query(Entity.id, Entity.title)
    data = [{"PID": id, "title": title} for (id, title) in entities]
    return json.dumps({"data": data})


@csrf.exempt
@app.route("/api/entity", methods=["POST"])
@check_privilege
def create_entity():
    form = EntityForm(csrf_enabled=False)
    if form.validate_on_submit():
        try:
            ent = Entity(type=form.type.data,
                         title=form.title.data,
                         id=form.id.data)
        except EntityPIDExistsException:
            return '{"errors":[{"title": "Duplicate ID for entity"}]}', 409
        except EntityCollisionException:
            return json.dumps({'errors':
                 [{'title': 'ID Collision',
                   'detail': 'The provided ID collides with the existing ID \'%s\'' %
                             e.original_id}]}), 409
        db.session.add(ent)
        db.session.flush()
        db.session.add(Data(ent.id, 'html'))
        db.session.add(Representation(ent.id, 1, reference=True))
        db.session.commit()
        log(ent.id, "Created entity `%s'" % ent)
        data = {'documents': [doc.id for doc in ent.documents],
                'domain': app.config['BASE_URL'],
                'id': ent.id,
                'persistentURIs': ent.persistent_uris,
                'title': ent.title,
                'type': ent.type}
        return json.dumps({'data': data}), 201
    errors = [{'title': 'Malformed parameter',
               'detail': 'Field %s: %s' % (field, ' '.join(error))}
              for field, error in form.errors.iteritems()]
    return json.dumps({'errors': errors}), 400


@csrf.exempt
@app.route("/api/entity/<id>", methods=["GET"])
@check_privilege
def get_entity(id):
    ent = Entity.query.filter(Entity.id == id).first()
    if ent:
        data = {'documents': [doc.id for doc in ent.documents],
                'domain': app.config['BASE_URL'],
                'id': ent.id,
                'persistentURIs': ent.persistent_uris,
                'title': ent.title,
                'type': ent.type}
        return json.dumps({'data': data})
    else:
        return '{"errors":[{"title": "Entity not found"}]}', 404


@csrf.exempt
@app.route("/api/entity/<id>", methods=["PUT"])
@check_privilege
def update_entity(id):
    try:
        data = json.loads(request.data)
        validate(data, entity_schema)

        ent = Entity.query.filter(Entity.id == id).first()
        if not ent:
            return '{"errors":[{"title": "Entity not found"}]}', 404

        ent_str = str(ent)

        try:
            ent.id = data["id"]
            ent.title = data.get("title", "")
            ent.type = data["type"]
        except EntityPIDExistsException:
            db.session.rollback()
            return '{"errors":[{"title": "Duplicate ID for entity"}]}', 409
        except EntityCollisionException:
            db.session.rollback()
            return json.dumps({'errors':
                 [{'title': 'ID Collision',
                   'detail': 'The provided ID collides with the existing ID \'%s\'' %
                             e.original_id}]}), 409

        db.session.commit()
        log(ent.id, "Changed entity from `%s' to `%s'" % (ent_str, ent))

        data = {'documents': [doc.id for doc in ent.documents],
                'domain': app.config['BASE_URL'],
                'id': ent.id,
                'persistentURIs': ent.persistent_uris,
                'title': ent.title,
                'type': ent.type}
        return json.dumps({'data': data})
    except ValueError:
        return '{"errors":[{"title": "Malformed request",' \
               ' "detail":"Expected correctly formatted JSON data"}]}', 400
    except ValidationError as e:
        print e
        return '{"errors":[{"title": "Malformed request",' \
               ' "detail":"JSON data does not confirm to schema"}]}', 400


@csrf.exempt
@app.route("/api/entity/<id>", methods=["DELETE"])
@check_privilege
def delete_entity(id):
    ent = Entity.query.filter(Entity.id == id).first()
    if ent:
        db.session.delete(ent)
        db.session.commit()
        log(id, "Removed the entity `%s'" % ent)
        return "", 204
    else:
        return '{"errors":[{"title": "Entity not found"}]}', 404


@csrf.exempt
@app.route("/api/document", methods=["POST"])
@check_privilege
def create_document():
    try:
        data = json.loads(request.data)
        validate(data, document_schema)

        ent = Entity.query.filter(Entity.id == data['entity']).first()
        if not ent:
            return '{"errors":[{"title": "Entity not found"}]}', 400

        if data['type'] == 'data':
            docs = Data.query.filter(Document.entity_id == ent.id,
                                     Data.format == data['format']).all()
            if len(docs) != 0:
                return '{"errors":[{"title": "Duplicate data format for entity"}]}', 400
            doc = Data(ent.id, data['format'], data.get('url', ''),
                       data['enabled'], data.get('notes', ''))
        else:
            ref = Representation.query.filter(Document.entity_id == ent.id,
                                              Representation.reference == True).first()
            if data['reference']:
                if ref:
                    ref.reference = False
            elif not ref:
                return '{"errors":[{"title": "Reference error",' \
                       ' "detail":"At least one reference representation is required"}]}', 400

            highest = Representation.query.\
                filter(Document.entity_id == ent.id).\
                order_by(Representation.order.desc()).first()
            if highest:
                order = highest.order + 1
            else:
                order = 1

            doc = Representation(ent.id, order, url=data.get('url', ''),
                                 label=data.get('label', ''), enabled=data['enabled'],
                                 notes=data.get('form', ''), reference=data['reference'])

        db.session.add(doc)
        db.session.commit()
        log(doc.entity_id, "Added %s document `%s'" % (data['type'], doc))

        return json.dumps({'data': doc.to_dict()}), 201
    except ValueError:
        return '{"errors":[{"title": "Malformed request",' \
               ' "detail":"Expected correctly formatted JSON data"}]}', 400
    except ValidationError:
        return '{"errors":[{"title": "Malformed request",' \
               ' "detail":"JSON data does not confirm to schema"}]}', 400


@csrf.exempt
@app.route("/api/document/<id>", methods=["GET"])
@check_privilege
def get_document(id):
    doc = Document.query.filter(Document.id == id).first()
    if not doc:
        return '{"errors":[{"title":"Document not found"}]}', 404
    return json.dumps({'data': doc.to_dict()})


def update_data(data, doc):
    docs = Data.query.filter(Document.entity_id == doc.entity_id,
                             Data.format == data['format']).all()
    if len(docs) != 0:
        db.session.rollback()
        return '{"errors":[{"title": "Duplicate data format for entity"}]}', 400

    doc.format = data["format"]
    db.session.commit()

    return json.dumps({'data': doc.to_dict()})


def update_representation(data, doc):
    ref = Representation.query.filter(Document.entity_id == doc.entity_id,
                                      Representation.reference == True).first()
    if data["reference"]:
        if ref:
            ref.reference = False
        doc.reference = True
    elif not ref:
        db.session.rollback()
        return '{"errors":[{"title": "Reference error",' \
               ' "detail":"At least one reference representation is required"}]}', 400

    if 'order' in data and doc.order != data['order']:
        old_order = doc.order
        new_order = data['order']
        if new_order <= 0:
            db.session.rollback()
            return '{"errors":[{"title": "Order error",' \
                   ' "detail":"Order must be larger than or equal to 1"}]}', 400

        max_order = Representation.query.filter(Document.entity_id == doc.entity_id).count()
        if new_order > max_order:
            db.session.rollback()
            return '{"errors":[{"title": "Order error",' \
                   ' "detail":"Order too high"}]}', 400

        docs = Representation.query.filter(Document.entity_id == doc.entity_id,
                                           Representation.order <= max(new_order, old_order),
                                           Representation.order >= min(new_order, old_order))\
            .order_by(Representation.order.asc()).all()
        op = operator.add if new_order < old_order else operator.sub

        for d in docs:
            d.order = op(d.order, 1)

        doc.order = new_order

    db.session.commit()
    return json.dumps({'data': doc.to_dict()})


@csrf.exempt
@app.route("/api/document/<id>", methods=["PUT"])
@check_privilege
def update_document(id):
    try:
        data = json.loads(request.data)
        validate(data, document_schema)

        doc = Document.query.filter(Document.id == id).first()
        if not doc:
            return '{"errors":[{"title": "Document not found"}]}', 404

        doc.enabled = data["enabled"]
        doc.url = data.get('url', '')
        doc.notes = data.get('notes', '')

        if data['type'] == 'data':
            return update_data(data, doc)
        else:
            return update_representation(data, doc)
    except ValueError:
        return '{"errors":[{"title": "Malformed request",' \
               ' "detail":"Expected correctly formatted JSON data"}]}', 400
    except ValidationError:
        return '{"errors":[{"title": "Malformed request",' \
               ' "detail":"JSON data does not confirm to schema"}]}', 400


@csrf.exempt
@app.route("/api/document/<id>", methods=["DELETE"])
@check_privilege
def delete_document(id):
    doc = Document.query.filter(Document.id == id).first()
    if not doc:
        return '{"errors":[{"title":"Document not found"}]}', 404
    if isinstance(doc, Representation):
        if doc.reference:
            count = Representation.query.\
                filter(Document.entity_id == doc.entity_id).count()
            if count > 1:
                return '{"errors":[{"title":"Can not delete reference representation"}]}', \
                       409
            db.session.delete(doc)
            db.session.flush()
        i = 1
        reps = Representation.query.\
               filter(Document.entity_id == doc.entity_id).\
               order_by(Representation.order.asc()).all()
        for rep in reps:
            rep.order = i
            i += 1
    else:
        db.session.delete(doc)
    log(doc.entity_id, "Removed the document '%s' %s" %
        (doc, doc.entity))
    db.session.commit()
    return "", 204