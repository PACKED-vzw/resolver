#!/bin/bash

service mysql start

if [ ! -f sentinel ]; then
    echo "Initializing..."
    python check_config.py
    python initialise.py
    touch sentinel
fi

exec gunicorn -w $GUNICORN_WORKERS -b 0.0.0.0:80 resolver:wsgi_app
