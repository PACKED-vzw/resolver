from setuptools import setup
from os import path

def read(fname):
    return open(path.join(path.dirname(__file__), fname)).read()

setup(
    name='resolver',
    version='0.9.0',
    packages=['resolver', 'resolver.model', 'resolver.controllers'],
    url='https://github.com/PACKED-vzw/resolver',
    license='GPL v3',
    author='Packed vzw',
    author_email='pieter@packed.be',
    description='The Resolver application is a tool for creating, managing, and using persistent URIs.',
    long_description=read ('README.md'),
    include_package_data=True,
    package_data={
        'config':'resolver.cfg'
    },
    scripts=[
        'bin/initialise.py'
    ],
    install_requires=[
        'BeautifulSoup == 3.2.1',
        'Flask == 0.10.1',
        'Flask-SQLAlchemy == 1.0',
        'Flask-WTF == 0.10.0',
        'Jinja2 == 2.7.3',
        'MarkupSafe == 0.23',
#        'MySQL-python == 1.2.5',
        'SQLAlchemy == 0.9.7',
        'Unidecode == 0.04.16',
        'WTForms == 2.0.1',
        'Werkzeug == 0.9.6',
        'gunicorn == 19.1.0',
        'itsdangerous == 0.24',
        'requests == 2.3.0',
        'wsgiref == 0.1.2'
    ]
)
