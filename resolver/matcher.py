import re
from resolver import app
from resolver.model import document_types, entity_types
from resolver.exception import NotFoundException

patterns = {'%dtype': '/(?P<dtype>%s)' % '|'.join(document_types),
            '%etype': '/(?P<etype>%s)' % '|'.join(entity_types),
            #'%id': '(?P<id>[0-9]+)',
            '%id': '/(?P<id>[^/]+)',
            '%slug': '(/(?P<slug>[^/]+)|)'}
            #'%slug': '(?P<slug>[^/]+)'}

def compile_template(template):
    splitted = template.split('/')
    pattern = [(patterns[part] if (part in patterns) else ('/'+part))
               for part in splitted]
    # [1:] to remove the leading slash
    return re.compile(''.join(pattern)[1:]+'\Z').match

class Template(object):
    def __init__(self, pattern):
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

def simple_template_valid(template):
    # A valid template has either:
    #   - %id
    #   - %id, %slug
    opts = re.findall('(?:(%.+?)(?:/|\Z))', template)

    if len(opts)==1:
        return '%id' in opts
    elif len(opts)==2:
        return ('%id' in opts) and ('%slug' in opts)

    return False

def full_template_valid(template):
    # A valid template has either:
    #   - %id, %dtype
    #   - %id, %dtype, %slug
    #   - %id, %dtype, %etype
    #   - %id, %dtype, %etype, %slug
    opts = opts = re.findall('(?:(%.+?)(?:/|\Z))', template)

    if not ('%id' in opts and '%dtype' in opts):
        return False
    elif len(opts)==2:
        return True
    elif len(opts)==3:
        return ('%etype' in opts or '%slug' in opts)
    elif len(opts)==4:
        return ('%etype' in opts and '%slug' in opts)

    return False

if not simple_template_valid(app.config['SIMPLE_URL']):
    raise Exception("SIMPLE_URL template invalid")

if not full_template_valid(app.config['FULL_URL']):
    raise Exception("FULL_URL template invalid")

matcher = Matcher([Template(app.config['SIMPLE_URL']),
                   Template(app.config['FULL_URL'])])
