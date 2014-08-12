from resolver.config import Config

if (Config.SALT == "") or (Config.SECRET_KEY == ""):
    import os
    from base64 import b64encode
    with open('docker_config.py', 'w') as f:
        f.write("SECRET_KEY = '%s'\n" % b64encode(os.urandom(64)))
        f.write("SALT = '%s'" % b64encode(os.urandom(64)))
