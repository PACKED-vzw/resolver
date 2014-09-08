Resolver
========

## About
The Resolver application is a tool for creating, managing, and using *persistent URIs*. More information on the usage of the tool and its purpose can be found on the [wiki](https://github.com/PACKED-vzw/resolver/wiki).

## Information for developers
The application was built using the [Flask](http://flask.pocoo.org/) microframework, using several common extensions such as `Flask-SQLAlchemy` for interaction with databases, and `Flask-WTF` for form validation. All code is contained inside the `resolver` directory, with all data models inside `resolver/model` and all controller/view functions inside `resolver/controllers`.

To contribute to the application, first follow the installation instructions to set up your development environment. The code is pretty straight-forward and mostly self-explanatory. Flask has some [great documentation](http://flask.pocoo.org/docs/) that should help you getting started in no time.

## Installation

See `INSTALL.md` for instructions.
