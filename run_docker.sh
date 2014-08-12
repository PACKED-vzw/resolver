#!/bin/bash

service mysql start

if [ ! -f sentinel ]; then
    echo "Initializing..."
    python check_config.py
    python initialise.py
    touch sentinel
fi

export RESOLVER_SETTINGS=`pwd`/docker_config.py

exec gunicorn -w 4 -b 0.0.0.0:80 resolver:wsgi_app
