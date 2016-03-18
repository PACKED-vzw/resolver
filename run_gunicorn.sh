#!/bin/bash

if [ -d "venv" ]; then
    source venv/bin/activate
fi

exec gunicorn -c gunicorn/resolver.cfg resolver:wsgi_app
