#!/bin/bash

service mysql start
exec gunicorn -w 2 -b 0.0.0.0:80 resolver:app
