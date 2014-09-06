from resolver.database import db, init_db
from resolver.model import User
import resolver.kvstore as kvstore

init_db()
db.session.add(User("admin", "default"))
db.session.commit()

kvstore.set('titles_enabled', True)
kvstore.set('default_notice', 'ToDo')
kvstore.set('default_notice_clean', 'ToDo')
kvstore.set('logo_url', False)
kvstore.set('domains', '')
