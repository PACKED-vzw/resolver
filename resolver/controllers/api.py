from flask import redirect, request, render_template, flash, session, Response, g
from resolver.modules.views.rest import RestApi, ErrorRestApi
from functools import update_wrapper
import json
from jsonschema import validate, ValidationError
from flask.ext.login import login_user, logout_user, current_user, login_required
import operator
from resolver import app, lm
from resolver.exception import *
from resolver.model import *
from resolver.model.user import pwd_context
from resolver.model.schemas import *
from resolver.database import db
from resolver.forms import SigninForm, EntityForm
from resolver.modules.views.api.entity import EntityViewApi
from resolver.util import log
from resolver import csrf


def requires_authentication():
    return Response(
        'Could not verify your access level for that URL.\n'
        'Log in using proper credentials.', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )


def check_authorization(username, password):
    user = User.query.filter(User.username == username).first()
    if not user:
        return requires_authentication()
    return pwd_context.verify(password, user.password)


def check_privilege(func):
    """
    Use Basic authentication
    :param func:
    :return:
    """

    def inner(*args, **kwargs):
        auth = request.authorization

        # Kept for backwards compatibility
        if not auth and g.user is not None:
            if g.user.is_authenticated:
                return func(*args, **kwargs)
            else:
                redirect('/resolver/api/login', 401)

        if not auth or not check_authorization(auth.username, auth.password):
            return requires_authentication()
        return func(*args, **kwargs)

    return update_wrapper(inner, func)


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request
def before_request():
    g.user = current_user


def old_login(func):
    def inner(*args, **kwargs):
        if current_user.is_authenticated:
            return func(*args, **kwargs)
        else:
            return redirect("/resolver/api/login", 401)

    # func.provide_automatic_options = False
    return update_wrapper(inner, func)


##
# Deprecated routes
@csrf.exempt
@app.route('/resolver/api/login', methods=["POST"])
def depr_login():
    if g.user is not None and g.user.is_authenticated:
        return "", 204
    form = SigninForm(csrf_enabled=False)
    if form.validate_on_submit():
        user = User.query.filter(User.username == form.username.data).first()
        if not user:
            return ErrorRestApi().response(status=403, errors=['Username not found.'])
        login_user(user)
        return "", 204
    return ErrorRestApi().response(status=401, errors=['You need to provide a username and password.'])


@app.route("/resolver/api/logout")
@old_login
def depr_logout():
    logout_user()
    return redirect("/resolver/api/login")


#
##


@csrf.exempt
@app.route("/resolver/api/entity", methods=["GET"])
def get_entities():
    entities = db.session.query(Entity.id, Entity.title)
    data = [{"PID": pid, "title": title} for (pid, title) in entities]
    return RestApi().response(data={'data': data})


@csrf.exempt
@app.route("/resolver/api/entity", methods=["POST"])
@check_privilege
def create_entity():
    form = EntityForm(csrf_enabled=False)
    if form.validate_on_submit():
        try:
            ent = Entity(type=form.type.data,
                         title=form.title.data,
                         id=form.id.data)
        except EntityPIDExistsException:
            return ErrorRestApi().response(status=409, errors=['Duplicate ID for entity.'])
        except EntityCollisionException as e:
            return ErrorRestApi().response(status=409, errors=[{
                'title': 'ID Collision',
                'detail': 'The provided ID \'{0}\' collides with the existing ID \'{1}\''.format(form.id.data,
                                                                                                 e.original_id)
            }])
        db.session.add(ent)
        db.session.flush()
        db.session.add(Data(ent.id, 'html'))
        db.session.add(Representation(ent.id, 1, reference=True))
        db.session.commit()
        log(ent.id, "Created entity `%s'" % ent)
        return RestApi().response(status=201, data={'data': EntityViewApi().output(entity=ent)})
    errors = [{'title': 'Malformed parameter',
               'detail': 'Field %s: %s' % (field, ' '.join(error))}
              for field, error in form.errors.iteritems()]
    return ErrorRestApi().response(status=400, errors=errors)


@csrf.exempt
@app.route("/resolver/api/entity/<id>", methods=["GET"])
def get_entity(id):
    out_data = EntityViewApi().get(id)
    if out_data:
        return RestApi().response(data={'data': out_data})
    else:
        return ErrorRestApi().response(status=404, errors=['Entity not found.'])


@csrf.exempt
@app.route('/resolver/api/entity/original/<string:original_id>', methods=['GET'])
def get_entity_by_original_id(original_id):
    out_data = EntityViewApi().get_original(original_id)
    if out_data:
        return RestApi().response(data={'data': out_data})
    else:
        return ErrorRestApi().response(status=404, errors=['Entity not found.'])


@csrf.exempt
@app.route("/resolver/api/entity/<id>", methods=["PUT"])
@check_privilege
def update_entity(id):
    # With form-data, you also get the boundary after the first ';'
    content_type = request.headers['Content-Type'].split(';')
    if content_type[0] == 'application/x-www-form-urlencoded' \
            or content_type[0] == 'multipart/form-data':
        form = EntityForm(csrf_enabled=False)
        data = {
            'id': form.id.data,
            'title': form.title.data,
            'type': form.type.data
        }
    else:
        try:
            data = json.loads(request.data)
            validate(data, entity_schema)
        except ValueError as e:
            errors = [{
                'title': 'Malformed request',
                'detail': 'Expected correctly formatted JSON data: {0}'.format(e)
            }]
            return ErrorRestApi().response(status=400, errors=errors)
        except ValidationError as e:
            errors = [{
                'title': 'Malformed request',
                'detail': 'JSON data does not conform to schema: {0}'.format(e)
            }]
            return ErrorRestApi().response(status=400, errors=errors)

    ent = Entity.query.filter(Entity.id == id).first()
    if not ent:
        return ErrorRestApi().response(status=404, errors=['Entity not found.'])

    ent_str = str(ent)

    try:
        ent.id = data["id"]
        ent.title = data.get("title", "")
        ent.type = data["type"]
    except EntityPIDExistsException:
        db.session.rollback()
        return ErrorRestApi().response(status=409, errors=['Duplicate ID \'{0}\' for entity.'.format(data['id'])])
    except EntityCollisionException as e:
        db.session.rollback()
        errors = [{
            'title': 'ID collision',
            'detail': 'The provided ID \'{0}\' collides with the existing ID \'{0}\'.'.format(data['id'], e.original_id)
        }]
        return ErrorRestApi().response(status=409, errors=errors)

    db.session.commit()
    log(ent.id, "Changed entity from `%s' to `%s'" % (ent_str, ent))

    return RestApi().response(data={'data': EntityViewApi().output(entity=ent)})


@csrf.exempt
@app.route("/resolver/api/entity/<id>", methods=["DELETE"])
@check_privilege
def delete_entity(id):
    ent = Entity.query.filter(Entity.id == id).first()
    if ent:
        db.session.delete(ent)
        db.session.commit()
        log(id, "Removed the entity `%s'" % ent)
        return "", 204
    else:
        return ErrorRestApi().response(status=404, errors=['Entity not found.'])


@csrf.exempt
@app.route("/resolver/api/document", methods=["POST"])
@check_privilege
def create_document():
    try:
        data = json.loads(request.data)
        validate(data, document_schema)

        ent = Entity.query.filter(Entity.id == data['entity']).first()
        if not ent:
            return ErrorRestApi().response(status=400, errors=['Entity not found.'])

        if data['type'] == 'data':
            docs = Data.query.filter(Document.entity_id == ent.id,
                                     Data.format == data['format']).all()
            if len(docs) != 0:
                return ErrorRestApi().response(status=400, errors=['Duplicate data format \'{0}\' for entity.'
                                               .format(data['format'])])
            doc = Data(ent.id, data['format'], data.get('url', ''),
                       data['enabled'], data.get('notes', ''))
        else:
            ref = Representation.query.filter(Document.entity_id == ent.id,
                                              Representation.reference == True).first()
            if data['reference']:
                if ref:
                    ref.reference = False
            elif not ref:
                errors = [{
                    'title': 'Reference error',
                    'detail': 'At least one reference representation is required.'
                }]
                return ErrorRestApi().response(status=400, errors=errors)

            highest = Representation.query. \
                filter(Document.entity_id == ent.id). \
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

        return RestApi().response(status=201, data={'data': doc.to_dict()})
    except ValueError as e:
        errors = [{
            'title': 'Malformed request',
            'detail': 'Expected correctly formatted JSON data: {0}'.format(e)
        }]
        return ErrorRestApi().response(status=400, errors=errors)
    except ValidationError as e:
        errors = [{
            'title': 'Malformed request',
            'detail': 'JSON data does not conform to schema: {0}'.format(e)
        }]
        return ErrorRestApi().response(status=400, errors=errors)


@csrf.exempt
@app.route("/resolver/api/document/<id>", methods=["GET"])
def get_document(id):
    doc = Document.query.filter(Document.id == id).first()
    if not doc:
        return ErrorRestApi().response(status=404, errors=['Document not found.'])
    return RestApi().response(status=201, data={'data': doc.to_dict()})


def update_data(data, doc):
    docs = Data.query.filter(Document.entity_id == doc.entity_id,
                             Data.format == data['format']).all()
    if len(docs) != 0:
        db.session.rollback()
        return ErrorRestApi().response(status=400, errors=['Duplicate data format \'{0}\' for entity \'{1}\'.'
                                       .format(data['format'], doc.entity_id)])

    doc.format = data["format"]
    db.session.commit()

    return RestApi().response(status=200, data={'data': doc.to_dict()})


# TODO: this code for updating order etc should be model code
def update_representation(data, doc):
    ref = Representation.query.filter(Document.entity_id == doc.entity_id,
                                      Representation.reference == True).first()
    if data["reference"]:
        if ref:
            ref.reference = False
        doc.reference = True
    elif not ref:
        db.session.rollback()
        errors = [{
            'title': 'Reference error',
            'detail': 'At least one reference representation is required.'
        }]
        return ErrorRestApi().response(status=400, errors=errors)

    if 'order' in data and doc.order != data['order']:
        old_order = doc.order
        new_order = data['order']
        if new_order <= 0:
            db.session.rollback()
            errors = [{
                'title': 'Order error',
                'detail': 'Order must be larger than or equal to 1.'
            }]
            return ErrorRestApi().response(status=400, errors=errors)

        max_order = Representation.query.filter(Document.entity_id == doc.entity_id).count()
        if new_order > max_order:
            db.session.rollback()
            errors = [{
                'title': 'Order error',
                'detail': 'Order too high.'
            }]
            return ErrorRestApi().response(status=400, errors=errors)

        docs = Representation.query.filter(Document.entity_id == doc.entity_id,
                                           Representation.order <= max(new_order, old_order),
                                           Representation.order >= min(new_order, old_order)) \
            .order_by(Representation.order.asc()).all()
        op = operator.add if new_order < old_order else operator.sub

        for d in docs:
            d.order = op(d.order, 1)

        doc.order = new_order

    db.session.commit()
    return RestApi().response(status=200, data={'data': doc.to_dict()})


@csrf.exempt
@app.route("/resolver/api/document/<id>", methods=["PUT"])
@check_privilege
def update_document(id):
    try:
        data = json.loads(request.data)
        validate(data, document_schema)

        doc = Document.query.filter(Document.id == id).first()
        if not doc:
            return ErrorRestApi().response(status=404, errors=['Document not found.'])

        doc.enabled = data["enabled"]
        doc.url = data.get('url', '')
        doc.notes = data.get('notes', '')

        if data['type'] == 'data':
            return update_data(data, doc)
        else:
            return update_representation(data, doc)
    except ValueError as e:
        errors = [{
            'title': 'Malformed request',
            'detail': 'Expected correctly formatted JSON data: {0}'.format(e)
        }]
        return ErrorRestApi().response(status=400, errors=errors)
    except ValidationError as e:
        errors = [{
            'title': 'Malformed request',
            'detail': 'JSON data does not conform to schema: {0}'.format(e)
        }]
        return ErrorRestApi().response(status=400, errors=errors)


@csrf.exempt
@app.route("/resolver/api/document/<id>", methods=["DELETE"])
@check_privilege
def delete_document(id):
    doc = Document.query.filter(Document.id == id).first()
    if not doc:
        return ErrorRestApi().response(status=404, errors=['Document not found.'])
    if isinstance(doc, Representation):
        if doc.reference:
            count = Representation.query. \
                filter(Document.entity_id == doc.entity_id).count()
            if count > 1:
                return ErrorRestApi().response(status=409, errors=['Can not delete reference representation.'])
            db.session.delete(doc)
            db.session.flush()
        i = 1
        reps = Representation.query. \
            filter(Document.entity_id == doc.entity_id). \
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
