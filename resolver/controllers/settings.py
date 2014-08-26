from flask import flash, redirect, render_template
from resolver import app
from resolver.controllers.user import check_privilege
from resolver.forms import SettingsForm
import resolver.kvstore as kvstore

@app.route('/resolver/settings')
@check_privilege
def admin_settings(form=None):
    if not form:
        form = SettingsForm(data={'default_notice':kvstore.get('default_notice'),
                                  'titles_enabled':kvstore.get('titles_enabled'),
                                  'logo_url':kvstore.get('logo_url')})

    return render_template('resolver/settings.html', title='Settings',
                           form=form)

@app.route('/resolver/settings', methods=["POST"])
@check_privilege
def admin_update_settings():
    form = SettingsForm()
    if form.validate():
        kvstore.set('default_notice', form.default_notice.data)
        kvstore.set('titles_enabled', form.titles_enabled.data)
        kvstore.set('logo_url', form.logo_url.data)
        flash("Settings successfully changed.", 'success')
        return admin_settings()
    else:
        return admin_settings(form=form)
