#!/bin/bash

service mysql start
exec gunicorn -w 4 -b 0.0.0.0:80 resolver:app
