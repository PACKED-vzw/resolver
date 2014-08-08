import re
from resolver import app
from resolver.model import document_types, object_types
from resolver.exception import NotFoundException

patterns = {'%dtype': '/(?P<dtype>%s)' % '|'.join(document_types),
            '%otype': '/(?P<otype>%s)' % '|'.join(object_types),
            #'%id': '(?P<id>[0-9]+)',
            '%id': '/(?P<id>[^/]+)',
            '%slug': '(/(?P<slug>[^/]+)|)'}
            #'%slug': '(?P<slug>[^/]+)'}

def valid_template(template):
    # A valid template has either:
    #   - %id only
    #   - %id, %otype, and %dtype
    #   - %id, %otype, %dtype, and %slug
    parts = template.split('/')
    return bool(re.compile("%id").search(template) or
                (re.compile("%dtype").search(template) and
                 re.compile("%otype").search(template) and
                 re.compile("%id").search(template)) or
                (re.compile("%dtype").search(template) and
                 re.compile("%otype").search(template) and
                 re.compile("%id").search(template) and
                 re.compile("%slug").search(template)))

def compile_template(template):
    splitted = template.split('/')
    pattern = [(patterns[part] if (part in patterns) else ('/'+part))
               for part in splitted]
    # [1:] to remove the leading slash
    return re.compile(''.join(pattern)[1:]+'\Z').match

class Template(object):
    def __init__(self, pattern):
        if not valid_template(pattern):
            raise Exception("URL Template invalid")

        self.__matcher__ = compile_template(pattern)

    def match(self, str):
        result = self.__matcher__(str)
        if result:
            return result.groupdict()
        raise None

class Matcher(object):
    def __init__(self, templates):
        self.__templates__ = templates

    def match(self, str):
        for t in self.__templates__:
            try:
                dict = t.match(str)
                return dict
            except:
                pass

        raise NotFoundException()

matcher = Matcher([Template(app.config['SIMPLE_URL']),
                   Template(app.config['FULL_URL'])])
