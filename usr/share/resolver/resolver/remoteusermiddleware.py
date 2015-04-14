class RemoteUserMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        user = environ.pop('HTTP_X_FORWARDED_FOR', None)
        if user:
            environ['REMOTE_ADDR'] = user
        return self.app(environ, start_response)
