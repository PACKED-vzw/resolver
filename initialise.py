from resolver.database import db, init_db
from resolver.model import User
import resolver.kvstore as kvstore

init_db()
db.session.add(User("admin", "default"))
db.session.commit()

kvstore.set('title_enabled', True)
