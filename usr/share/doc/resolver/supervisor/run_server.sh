#!/bin/bash

if [ "$1" == "" -o "$2" == "" -o "$3" == "" -o "$4" == "" ]; then
	echo "Error: parameter missing. Invoke as $0 [server_name] [proxy_name] [port] [resolver-dir]"
	exit 1
fi

c_dir="$4"
server_name="$1"
proxy_name="$2"
port="$3"

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

#exec gunicorn -w 4 -b 127.0.0.1:8080 resolver:wsgi_app
exec gunicorn -w 4 -b "$proxy_name"":""$port" resolver:wsgi_app
exit 0
