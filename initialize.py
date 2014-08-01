from resolver.database import db_session, init_db
from resolver.model import PersistentObject, Document, User

init_db()
db_session.add(User("admin", "default"))
db_session.commit()
