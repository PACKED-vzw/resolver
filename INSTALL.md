Installation instructions
=========================
In this document instructions are given to install the application on several platforms. The default login for every installation is `u: admin/p: default`. **Important:** change the password of the `admin` user immediately after installation.

## Linux/UNIX

### Requirements
The following packages should be installed on your system:
- mysql-server
- Python2
- python-virtualenv (optional, but highly recommended)
- A webserver such as Apache, nginx, ...

Additional packages such as `libmysqlclient-dev` (on Debian/Ubuntu) might be required to install some of the required Python packages.

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
4. Configure the application (see section `Configuration` further on)
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

Using the `-e` flag it is possible to set environment variables inside the container to configure the application. Setting the `BASE_URL` environment variable will change the application's configuration to use the provided value as base url for the application. It is also possible to change the default amount of Gunicorn workers (4) by setting `GUNICORN_WORKERS`. Example:
```
docker run -d -p 8080:80 -e "BASE_URL=http://resolver.be" -e "GUNICORN_WORKERS=2" packed/resolver
```

### Building your own image
It is possible to build a resolver image yourself. Just checkout the `docker` branch from the repository (`git checkout docker`) to gain access to the Dockerfile.

The image can be built like any other.

## Heroku
The application can be deployed on multiple PaaS services, but as an example instructions for Heroku are given. Some knowledge of Git is required for using Heroku.

1. Make sure you have an Heroku account, you have installed the command line tools, and you are logged in to Heroku using the tools ([more info...](https://devcenter.heroku.com/))
2. Clone the repository, go to the resolver directory, and create a new branch
```
$ git clone https://github.com/PACKED-vzw/resolver.git
$ cd resolver
$ git branch heroku
$ git checkout heroku
```
3. Create a new Heroku application
```
$ heroku create
```
4. Create a configuration file as explained in the configuration section, and commit your changes to the repository (note: you do not need to change anything in the database section).
5. Update the requirements for Heroku and commit your changes
```
$ echo "\npsycopg2" >> requirements.txt
```
6. Add a database to the application
```
$ heroku addons:add heroku-postgresql
```
7. Set the right environment variables
```
$ heroku config:set HEROKU=1
```
8. Push the application to heroku (notice how we are pushing our local branch `heroku` as the `master` branch in Heroku's remote repository)
```
$ git push heroku heroku:master
```
9. Initialise the application
```
$ heroku run python initialise.py
```
10. Configure 1 dyno
```
$ heroku ps:scale web=1
```

## Configuration
### Resolver
You can create a new configuration file by simply copying the `resolver.cfg.example` to `resolver.cfg` and editing it. Both `secret_key` and `salt` should contain two random strings of characters. The site [random.org](http://random.org/strings) can be used to generate random data. It is important that the value of `salt` remains constant as changing it will invalidate all user passwords!

The `DATABASE_*` values are the connection details for MySQL.

The value for `BASE_URL` should be the root URL of the application.

### Webserver
When running the application on a dedicated domain or subdomain, no special configuration is needed and the provided example configurations for Apache and nginx can be used.

When the application is hosted on the same domain as an existing application, for instance a simple PHP CMS installation, special configuration is needed in order to route the correct requests to the application. Specifically, all requests to `/resolver`, `/static`, and `/collection` should be forwarded to the application, making sure no parts of the request URI are truncated.

On Apache2 [mod_proxy](https://httpd.apache.org/docs/2.2/mod/mod_proxy.html) can be used. Similary, Nginx has [http_proxy](http://nginx.org/en/docs/http/ngx_http_proxy_module.html).
