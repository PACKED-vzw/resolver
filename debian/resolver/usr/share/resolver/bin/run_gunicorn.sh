#!/bin/bash

if [ -d "venv" ]; then
    source venv/bin/activate
fi

exec gunicorn -w 4 -b 127.0.0.1:8080 resolver:wsgi_app --timout 900 --graceful-timeout 900
