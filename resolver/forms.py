from flask_wtf import Form
from wtforms import StringField, SelectField, BooleanField,\
    PasswordField, TextAreaField, validators
from resolver.model import object_types, document_types

class ObjectForm(Form):
    id = StringField('ID', [validators.required()])
    title = StringField('Title', [validators.optional()])
    type = SelectField('Type', [validators.required()],
                       choices=zip(object_types,
                                   map(lambda c: c.capitalize(),
                                       object_types)))

class DocumentForm(Form):
    # TODO: URL not required
    url = StringField('URL', [validators.optional(), validators.URL()])
    type = SelectField('Type', [validators.required()],
                       choices=zip(document_types,
                                   map(lambda c: c.capitalize(),
                                       document_types)))
    enabled = BooleanField('Enabled', default=True)
    notes = TextAreaField('Notes', [validators.optional()])

class SigninForm(Form):
    username = StringField('Username', [validators.required(),
                                        validators.Length(min=3, max=32)])
    password = PasswordField('Password', [validators.required()])

class UserForm(SigninForm):
    confirm = PasswordField('Confirm', [validators.required()])
