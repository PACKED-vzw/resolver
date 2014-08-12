from resolver.database import db, init_db
from resolver.model import User

init_db()
db.session.add(User("admin", "default"))
db.session.commit()
