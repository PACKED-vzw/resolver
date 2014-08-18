class Config(object):
    # Root URL of the resolver, without trailing /, and with scheme.
    # e.g.: http://resolver.be
    BASE_URL = ""

    DATABASE_HOST = "127.0.0.1"
    DATABASE_USER = "root"
    DATABASE_PASS = ""
    DATABASE_NAME = "resolver"

    SECRET_KEY = "a"
    SALT = "a"

    # SIMPLE_URL should contain %id, may contain %slug
    SIMPLE_URL = "collection/%id"
    # FULL_URL should contain %dtype and %id, preferably also %slug and %etype
    FULL_URL = "collection/%etype/%dtype/%id/%slug"
