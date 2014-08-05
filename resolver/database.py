from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from resolver import app

engine = create_engine('mysql://%s:%s@%s/%s' %
                       (app.config['DATABASE_USER'], app.config['DATABASE_PASS'],
                        app.config['DATABASE_HOST'], app.config['DATABASE_NAME']),\
                       convert_unicode=True, pool_recycle=3600)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import resolver.model
    Base.metadata.create_all(bind=engine)
