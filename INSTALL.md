Installation instructions
=========================

This documents provides instructions to install the Resolver application on a Linux/UNIX based environment.

## Table of contents

1. Overview
2. Installation instructions
3. Deployment to a PaaS service

## Overview

The Resolver application is not a stand-alone application. It's part of a stack of required services. The setup is Web Server Gateway Interface (WSGI) based and consists of these parts:

| Interpreter | Python |
| WSGI HTTP Server | Gunicorn |
| Database Server | MySQL or MariaDB |
| HTTP Server | NGinX or Apache |

The installation instructions will cover on a Virtual Private Server (VPS) which will only host the Resolver application. **If you plan to install the application on an enviroment which hosts any other type of service (Apache/PHP), be aware of potential dependency (version) conflicts between packages.** If configuration files already exist, settings described in this document should be integrated.

The installation instructions assume that all services are running on the same host.

## Requirements/Dependencies

The instructions target intallation on an Ubuntu/Debian based system. You will need SSH or terminal access and appropriate system permissions to execute the following commands.

Update your system

```bash
sudo apt-get update
sudo apt-get upgrade
```

Install dependencies and packages

Essential build tools:

```bash
sudo apt-get install -y tar git wget build-essential vim
```

Python:

```bash
sudo apt-get install -y python python-dev python-virtualenv

MySQL with Python bindings

```bash
sudo apt-get install -y mysql-server python-mysqldb libmysqlclient-dev
```

## Create a new database

The Resolver application stores data in a MySQL/MariaDB database. Make sure you have the MySQL server running and sufficient access permissions to create a new database and user.  The following commands should be executed from the command line, but you can also create a new database/user via such tools as PHPMyAdmin or Sequel Pro.

In the following commands, change 'root' to the appropriate MySQL user.

Create a new database:

```bash
echo "CREATE DATABASE resolver CHARACTER SET utf8 COLLATE utf8_general_ci;" | mysql -u root -p
```

Create a new user with grant permissions for the database. This example will create a new database user `u:resolver` and `p:resolver`. Change these to a suitable user/password combination.

```bash
echo "CREATE USER 'resolver'@'localhost' IDENTIFIED BY 'resolver';" | mysql -u root -p
echo "GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, ALTER, CREATE TEMPORARY TABLES ON resolver.* TO 'resolver'@'localhost' IDENTIFIED BY 'resolver';" | mysql -u root -p
```

## Install the Resolver application

TBD: file system permissions and dedicated unix user

Deploy the codebase of the application. The instructions will install the application codebase in `/opt` but other locations, such as the home directory of a dedicated resolver user, are possible as well.

```bash
cd /opt
git clone https://github.com/PACKED-vzw/resolver.git resolver
```

You should end up with a new directory `/opt/resolver` which contains the application code.

### Virtual Enviroment

The application uses Python Virtual Environment to keep track of project specific library dependencies. First, we'll activate `venv`in the installation root.

```bash
cd /opt/resolver
virtualenv venv
. venv/bin/activate
```

Now install the required python packages using pip, Pythons' package manager tool which comes with Python 2.7.

```bash
pip install -r requirements.txt
```

### Configure the application settings file

Copy the example settings file and start editing this new file. In this example, we will use the `vi` editor.

```bash
cp resolver.cfg.example resolver.cfg
vi resolver.cfg
```

Change the `DATABASE_USER`, `DATABASE_PASS` and `DATABASE_NAME` variables to reflect the database and user we created in the previous section.

Change the `BASE_URL` variable to the domain location where the application will be active i.e. http://example.com. **The application will not listen directly to the root of the domain.**

Both `SECRET_KEY` and `SALT` should contain two random strings of characters. The site [random.org](http://random.org/strings) can be used to generate random data. It is important that the value of `SALT` remains constant as changing it will invalidate all user passwords!

### Initialise the database

This command will populate the database will all the required tables.

```bash
python initialise.py
```

## Configure the HTTP server

The HTTP server will act as a proxy for the Gunicorn HTTP WSGI server.
More information about HTTP proxies and WSGI can be found in the [Gunicorn documentation](http://gunicorn-docs.readthedocs.org/en/latest/deploy.html).

The next commands assume that the target domain (`resolver.be`) only serves the Resolver application. Generally, a target domain might already serve an existing CMS based website (Drupal, WordPress, etc.) In that case, you should add the following settings to an existing virtual host configuration instead of creating a new virtual host.

### NGinX

Install and start NGinX.

```bash
sudo apt-get install nginx
```

Create a new virtual host configuration for the resolver application and edit it using the `vi` editor.

```bash
sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/resolver.be
sudo vi /etc/nginx/sites-available/resolver.be
```

Change the `resolver.be` file so that it reflects the example settings below:

```
server {
	listen 80;

	# Make site accessible from http://resolver.be/
	# This is a catch-all domain configuration.
	# see: http://nginx.org/en/docs/http/server_names.html#miscellaneous_names
	server_name _;

	location / {
		proxy_pass		http://127.0.0.1:8080/;
		proxy_redirect		off;
		proxy_set_header	Host		$host;
		proxy_set_header	X-Real-IP	$remote_addr;
		proxy_set_header	X-Fowarded-For	$proxy_add_x_forwarded_for;
	}
}
```

Note: these settings assume that the Gunicorn daemon (see: next section) will run on port 8080.

Link the new configuration file to the `sites-enabled` folder:

```bash
sudo ln -s /etc/nginx/sites-available/resolver.local /etc/nginx/sites-enabled/
```

Restart NGinX.

```bash
sudo service nginx restart
```

### Apache

TBD

## Activate Gunicorn

You can start Gunicorn from the command line by this command running from the project root (`/opt/resolver`).

```bash
gunicorn -w 4 -b 127.0.0.1:8080 resolver:wsgi_app
```

Gunicorn will listen on port 8080 and make 4 workers available.

Gunicorn can be daemonized by using the `-D` or `--daemon` command line switch, although it might prove more useful to run the server by using `screen` or [Supervisor](http://supervisord.org/). An example configuration for Supervisor can be found in the `supervisor` directory.

## Deployment to a PaaS enviroment

### Docker

The application is also made available as a Docker image in the `packed/resolver` repository, and can be used to simplify the installation. The application's webserver is bound to port 80. Once again it is advised to run the application behind another webserver such as Apache or Nginx. See the `apache` and `nginx` directories for example configuration files.

To set up the application using Docker, one can run the following command as an example:
```
docker run -d -p 8080:80 -e "BASE_URL=http://resolver.be" -e "GUNICORN_WORKERS=2" packed/resolver
```
This will download the image, create a new container, execute the application, and forward all requests on `localhost:8080` to the resolver. The container will be configured to use 2 workers for Gunicorn.

Using the `-e` flag it is possible to set environment variables inside the container to configure the application. The `-e "GUNICORN_WORKERS=2"` option can be omitted; in this case the application will fall back to using 4 workers. The `-e "BASE_URL="` is mandatory however, and should be provided for the correct working of the application.

### Building your own image
It is possible to build a resolver image yourself, as the Dockerfile is provided in the repository.

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
$ echo "psycopg2==2.5.4" >> requirements.txt
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

### Webserver

When running the application on a dedicated domain or subdomain, no special configuration is needed and the provided example configurations for Apache and nginx can be used.

When the application is hosted on the same domain as an existing application, for instance a simple PHP CMS installation, special configuration is needed in order to route the correct requests to the application. Specifically, all requests to `/resolver`, `/static`, and `/collection` should be forwarded to the application, making sure no parts of the request URI are truncated.

On Apache2 [mod_proxy](https://httpd.apache.org/docs/2.2/mod/mod_proxy.html) can be used. Similary, Nginx has [http_proxy](http://nginx.org/en/docs/http/ngx_http_proxy_module.html).
