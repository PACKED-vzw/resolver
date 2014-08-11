from flask.ext.sqlalchemy import SQLAlchemy
from resolver import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@%s/%s' %\
                                        (app.config['DATABASE_USER'],
                                         app.config['DATABASE_PASS'],
                                         app.config['DATABASE_HOST'],
                                         app.config['DATABASE_NAME'])
db = SQLAlchemy(app)

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import resolver.model
    Base.metadata.create_all(bind=engine)
