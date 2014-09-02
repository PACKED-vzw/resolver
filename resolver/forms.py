from flask_wtf import Form
from wtforms import StringField, SelectField, BooleanField,\
    PasswordField, TextAreaField, DecimalField, validators
from resolver.model import entity_types, data_formats

class EntityForm(Form):
    id = StringField('ID', [validators.required()])
    title = StringField('Title', [validators.optional()])
    type = SelectField('Type', [validators.required()],
                       choices=zip(entity_types,
                                   map(lambda c: c.capitalize(),
                                       entity_types)))

class DocumentForm(Form):
    url = StringField('URL', [validators.optional(), validators.URL()])
    enabled = BooleanField('Enabled', default=True)
    notes = TextAreaField('Notes', [validators.optional()])

class DataForm(DocumentForm):
    format = SelectField('Type', [validators.required()],
                         choices=zip(data_formats,
                                     map(lambda f: f.capitalize(),
                                         data_formats)))

class RepresentationForm(DocumentForm):
    #order = DecimalField('Order', [validators.required(),
    #                               validators.NumberRange(min=1)])
    reference = BooleanField('Reference image', default=False)
    # TODO: Use constant var instead of constant val 64
    label = StringField('Label', [validators.optional(),
                                  validators.Length(max=64)])

class SigninForm(Form):
    username = StringField('Username', [validators.required(),
                                        validators.Length(min=3, max=32)])
    password = PasswordField('Password', [validators.required()])

class UserForm(SigninForm):
    confirm = PasswordField('Confirm', [validators.required()])

class SettingsForm(Form):
    default_notice = TextAreaField('Default notice', [validators.required()])
    titles_enabled = BooleanField('Titles enabled', default=True)
    logo_url = StringField('Logo URL', [validators.optional(), validators.URL()])
    domains = TextAreaField('Domains', [validators.optional()])
