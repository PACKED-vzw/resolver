class Config(object):
    DATABASE_HOST = "127.0.0.1"
    DATABASE_USER = "root"
    DATABASE_PASS = ""
    DATABASE_NAME = "resolver"
    SECRET_KEY = "changeme"
    SALT = "changemetoo"

    # SIMPLE_URL should only contain %id
    SIMPLE_URL = "collection/%id"
    # FULL_URL should contain %otype, %dtype, %id, and preferably also %slug
    FULL_URL = "collection/%otype/%dtype/%id/%slug"
