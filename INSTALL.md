Installation instructions
=========================
In this document instructions are given to install the application on several platforms. The default login for every installation is `u: admin/p: default`. **Important:** change the password of the `admin` user immediately after installation.

## Linux/UNIX

### Requirements
The following packages should be installed on your system:
- mysql-server
- Python2
- python-virtualenv

Additional packages such as `libmysqlclient-dev` (on Debian/Ubuntu) might be required to install some of the required Python packages

### Installation
1. Clone the git repository or extract the archive containing the source
2. Create a new virtual environment in the project directory and activate it
```
$ cd resolver
$ virtualenv venv
$ . venv/bin/activate
```
3. Install the required Python packages
```
pip install -r requirements.txt
```
4. Using your text editor of choice, change `resolver/config.py`
5. Initialize the database (and test if all settings are correct)
```
$ python initialise.py
```
6. The application should now be ready and can be ran by using Gunicorn. `[w]` should be replaced by the preferred amount of worker threads (2-4 should suffice), `[ip]:[port]` should be replaced by the IP and port on which the server should listen.
```
$ gunicorn -w [x] -b [ip]:[port] resolver:wsgi_app
```

It is highly advisable to use Gunicorn in combination with a webserver such as Apache or Nginx. Example configuration files for both servers can be found in the directories `apache` and `nginx`. When using Apache, Nginx, or any other proxying webserver, make sure the application is bound to the localhost IP only (127.0.0.1:[port]).

Gunicorn can be daemonized by using the `-D` or `--daemon` command line switch, although it might prove more useful to run the server by using `screen` or [Supervisor](http://supervisord.org/). An example configuration for Supervisor can be found in the `supervisor` directory.

## Docker
The application is also made available as a Docker image in the `packed/resolver` repository, and can be used to simplify the installation. The application's webserver is bound to port 80. Once again it is advised to run the application behind another webserver such as Apache or Nginx. See the `apache` and `nginx` directories for example configuration files.

For example:
```
docker run -d -p 8080:80 packed/resolver
```
Will download the image, create a new container, execute the application, and forward all requests on `localhost:8080` to the resolver. The image is configured to use 4 workers for Gunicorn.

## Heroku
