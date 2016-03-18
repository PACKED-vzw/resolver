#!/bin/bash

if [ "$1" != "" -a "$2" != "" -a "$3" == "" -a "$4" == "" ]; then
    # After v2.0.0, we changed to way this script is run. To save something
    # of backward compatibility, we accept calls where either two arguments are given
    # which we assume to be the resolver_name and the c_dir (new way)
    # or when 4 arguments are given (old way)
    # We ignore the configuration file if that happens
    c_dir="$2"
    server_name="$1"
else
    if [ "$1" == "" -o "$2" == "" -o "$3" == "" -o "$4" == "" ]; then
	echo "Error: parameter missing. Invoke as $0 [server_name] [proxy_name] [port] [resolver-dir]"
	c_dir="$4"
    server_name="$1"
    proxy_name="$2"
    port="$3"
	exit 1
fi
fi



if [ ! -d "$c_dir" ]; then
	echo "Error: resolver directory $c_dir does not exist!"
	exit 2
fi

cd "$c_dir"

if [ ! -f "$c_dir""/""resolver.cfg" ]; then
	echo "Error: resolver.cfg not found!"
	exit 0
fi

if [ ! -d "$c_dir""/""$server_name""/bin" ]; then
        virtualenv "$server_name"
        . "$server_name""/bin/activate"
else
        . "$server_name""/bin/activate"
fi

if "$proxy_name" != "" ]; then
    exec gunicorn -w 4 -b "$proxy_name"":""$port" resolver:wsgi_app --timeout 900 --graceful-timeout 900
else
    exec gunicorn -c "$c_dir/gunicorn/resolver.cfg" resolver:wsgi_app
fi



#exec gunicorn -w 4 -b 127.0.0.1:8080 resolver:wsgi_app

exit 0