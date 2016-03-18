Installation instructions
=========================

This documents provides instructions to install the Resolver application on a Linux/UNIX based environment.

## Overview

The Resolver project is a database driven web application based on the following technology stack:

| Type | Package | Version |
| --- | --- | --- |
| Interpreter | Python | >= 2.7 |
| WSGI HTTP Server | Gunicorn | 17.5 |
| Database Server | MySQL or MariaDB | >= 5.5 |
| HTTP Server | NGinX or Apache | N/A |
| Process manager | Supervisor | N/A |

The instructions are specifically geared towards a installation on a virtual private server (VPS) which exclusively hosts the Resolver. Contact your hosting provider to make sure your hosting plan covers the requirements outlined further in this document.

**If you plan to install the application on an environment which hosts any other type of services (Apache/PHP), be aware of potential dependency (version) conflicts between packages.**

The instructions target intallation on an [Ubuntu](http://www.ubuntu.com/) or [Debian](https://www.debian.org) based system.

The installation instructions assume that all services are running on the same host.

## Requirements

You will need SSH or terminal access and a user account with appropriate administrative permissions to execute the following commands. Packages might already be installed on your system.

We prepare the system by performing a system wide update of all packages:

```bash
sudo apt-get update
sudo apt-get upgrade
```

Now we are ready to install all the required packages and services.

Essential build tools:

```bash
sudo apt-get install -y tar git wget build-essential vim
```

Python:

```bash
sudo apt-get install -y python python-dev python-virtualenv gunicorn
```

MySQL with Python bindings

```bash
sudo apt-get install -y mysql-server python-mysqldb libmysqlclient-dev
```

## Create a new database

The Resolver application stores data in a MySQL/MariaDB database. Make sure you have the MySQL server running and sufficient access permissions to create a new database and user.  The following commands should be executed from the command line, but you can also create a new database/user via alternative, graphical MySQL clients.

In the following commands, you might change 'root' to an appropriate MySQL account with administrative privileges.

Create a new database called `resolver`:

```bash
echo "CREATE DATABASE resolver CHARACTER SET utf8 COLLATE utf8_general_ci;" | mysql -u root -p
```

Create a new user with grant permissions for the database. This example will create a new database user `u:resolver` with `p:resolver`. Change these to a suitable user/password combination.

```bash
echo "CREATE USER 'resolver'@'localhost' IDENTIFIED BY 'resolver';" | mysql -u root -p
echo "GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, ALTER, CREATE TEMPORARY TABLES ON resolver.* TO 'resolver'@'localhost' IDENTIFIED BY 'resolver';" | mysql -u root -p
```

## <a name="install">Install the Resolver application</a>

### Create a new unix user

The application runs through its own persistent daemon. For security purposes, we'll create a new dedicated unix user & group which will own this process.

```bash
sudo adduser resolver
```

### Deploy the codebase

Switch to the newly created resolver user and download the latest release.

```bash
su - resolver
curl https://codeload.github.com/PACKED-vzw/resolver/tar.gz/v1.6.1 | tar xvz
```

You should end up with a new directory `/home/resolver/resolver-1.6.1` which contains the application code.

### Virtual Enviroment

The application uses Python [Virtual Environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/) to keep track of project specific library dependencies. First, we'll activate `venv`in the installation root of the resolver application.

```bash
cd resolver
virtualenv venv
. venv/bin/activate
```

Now install the required python packages using pip, Pythons' package manager tool which comes with Python 2.7.

```bash
pip install -r requirements.txt
```

> Note that, if you are using supervisor (see below), the name of your virtual environment must be the same as the value of SERVER_NAME and RESOLVER_NAME. Otherwise, the application will fail.

### Configure the application settings file

Copy the example settings file and start editing this new file. In this example, we will use the `vi` editor.

```bash
cp resolver.cfg.example resolver.cfg
vi resolver.cfg
```

Change the `DATABASE_USER`, `DATABASE_PASS` and `DATABASE_NAME` variables to reflect the database and user we created in the previous section.

Change the `BASE_URL` variable to the domain location where the application will be active. (i.e. http://resolver.be).

Both `SECRET_KEY` and `SALT` should contain two random strings of characters. The site [random.org](http://random.org/strings) can be used to generate random data. It is important that the value of `SALT` remains constant as changing it will invalidate all user passwords!

### Initialise the database

This command will populate the database will all the required tables.

```bash
python initialise.py
```

## <a name="server">Configure the HTTP server</a>

The HTTP server will act as a proxy for the [Gunicorn HTTP WSGI server](http://gunicorn.org/).
More information about HTTP proxies and WSGI can be found in the [Gunicorn documentation](http://gunicorn-docs.readthedocs.org/en/latest/deploy.html).

On Apache2 [mod_proxy](https://httpd.apache.org/docs/2.2/mod/mod_proxy.html) can be used. Similary, Nginx has [http_proxy](http://nginx.org/en/docs/http/ngx_http_proxy_module.html).

The next commands assume that the target domain (i.e. `resolver.be`) only serves the Resolver application.  When the application is hosted on the same domain as an existing application, for instance a PHP CMS installation (Drupal, WordPress,...), special configuration is needed in order to route the correct requests to the application. Specifically, all requests to `/resolver`, `/static`, and `/collection` should be forwarded to the application, making sure no parts of the request URI are truncated.

If you are still logged in as the `resolver` user, log out and switch back to an user account with administrative privileges before proceeding.

### <a name="nginx">NGinX</a>

The following command installs and starts the NGinX HTTP service.

```bash
sudo apt-get install nginx
```

Create a new virtual host configuration for the resolver application and edit it using the `vi` editor.

```bash
sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/resolver.be
sudo vi /etc/nginx/sites-available/resolver.be
```

Change the `resolver.be` file so that it reflects the example settings below. This configuration will make NGinX behave as a catch all proxy, forwarding all HTTP calls to the Gunicorn HTTP WSGI server process.

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

Note: these settings assume that the Gunicorn process will run on port 8080 (see: next section)

Link the new configuration file to the `sites-enabled` folder:

```bash
sudo ln -s /etc/nginx/sites-available/resolver.be /etc/nginx/sites-enabled/
```

Restart NGinX.

```bash
sudo service nginx restart
```

### <a name="apache">Apache</a>

Install and start the apache2 service (Debian-based).

```bash
sudo aptitude install apache2
```

Load the proxy and proxy_http modules

```bash
sudo a2enmod proxy
sudo a2enmod proxy_http
```

Create a new virtual host configuration for the resolver application (in this case resolver.be) and edit it using the `nano` editor.

```bash
sudo nano /etc/apache2/sites-available/resolver.be.conf
```

Change the `resolver.be.conf` file so that it reflects the example settings below. This configuration will make apache redirect all requests to our gunicorn server running at port 8080 (see below).


```
<VirtualHost *:80>
        ServerName resolver.be

        LogLevel warn
        ErrorLog /var/log/apache2/resolver_error.log
        CustomLog /var/log/apache2/alpacafiles/resolver_access.log combined

        ProxyPass / http://127.0.0.1:8080/
        ProxyPassReverse / http://127.0.0.1:8080/
        ProxyPreserveHost On
</VirtualHost>

```

Enable the new website:

```bash
sudo a2ensite resolver.be.conf
```

Reload apache (reread configuration files).

```bash
sudo service apache2 reload
```


## <a name="gunicorn">The Gunicorn WSGI HTTP server</a>

All configuration options for Gunicorn are in a configuration file inside the `gunicorn` directory. Copy `resolver.cfg.example` to `resolver.cfg` and update the parameters to suit your installation. The default options will result in a working installation, but usually you will want to change the `proxy_name` and `proxy_port` settings.

```python
import multiprocessing
##
# Gunicorn configuration file
# See http://docs.gunicorn.org/en/latest/settings.html

# Address to bind to. By default it is localhost.
proxy_name = '127.0.0.1' # The address to bind to.
proxy_port = '8080' # The port to bind to.
bind = '{0}:{1}'.format(proxy_name, proxy_port)

# Workers
# Recommended: 2x CPU count + 1
workers = multiprocessing.cpu_count() * 2 + 1

# Timeout
# As the resolver sometimes parses large files, we set this to a minimum
# of 900 seconds (15 minutes). Increase if you get proxy errors and timeouts.
timeout = 900
graceful_timeout = 900
```

To start Gunicorn, you can either execute `run_gunicorn.sh` from the project root (e.g. `/home/resolver/resolver`) or start Gunicorn directly. Make sure you are logged in as the `resolver` user we've created earlier.

```bash
gunicorn -c gunicorn/resolver.cfg resolver:wsgi_app
```

### 1.6.x and earlier

You can start Gunicorn from the command line manually running by this command running the project root (`/home/resolver/resolver`). Make sure you are logged in as the `resolver` user we've created earlier.

```bash
gunicorn -w 4 -b 127.0.0.1:8080 resolver:wsgi_app
```

Gunicorn will listen on port 8080 and make 4 workers available.

If you close the terminal session, the process will be killed. Gunicorn can be daemonized by using the `-D` or `--daemon` command line switch, although it might prove more useful to run the server by using `screen` or [Supervisor](http://supervisord.org/).

## Performance

When working with large import files, performance can become an issue. If you run into trouble, alter these settings.

### 411 Request entity body too large

The import file is rejected by the HTTP proxy (Apache or NGinx) because it is too large. You can change the limitation in the configuration of the proxy.

**NGinX**

Open the configuration file `/etc/nginx/nginx.conf` and add this line to the `http` or `location` section of the file.

```
client_max_body_size 2M;
```

This allows uploads below 2M. Change the value to allow larger file uploads.

**Apache**

Open the configuration file for your virtual host server (e.g. resolver.be.conf) and add the following directive:

```
LimitRequestBody 2000000
```

[LimitRequestBody](http://httpd.apache.org/docs/current/mod/core.html#limitrequestbody) accepts any value in bytes. This value will allow uploads up to 2M. Change the value to allow larger file uploads.

### 502 Bad Gateway

This is a general error thrown by the HTTP proxy when it can't reach the gunicorn backend.

The gunicorn process execution has a time out period. Large file imports (ie 5000 rows) can cause gunicorn to time out. You can configure the timeout with the `--timeout` and `--graceful-timeout` flag followed by the interval expressed in seconds.

i.e. Set the timeout to 4 minutes or 240 seconds:

```
gunicorn -w 4 -b 127.0.0.1:8080 resolver:wsgi_app --timeout 240 --graceful-timeout 240
```

### 504 Bad Gateway

This error is thrown by the web server (nginx/apache) when it times out before the Gunicorn has had a chance to complete processing. You need to configure the time out setting of the web server to match it with the time out of the gunicorn backend.

**NGinX**

Open the configuration file of your resolver instance (ie. `/etc/nginx/sites-available/resolver.be`) and add this line to the `http` or `location` section of the file. The value should match teh timeout value of the gunicorn daemon.

```
proxy_read_timeout 300s;
```

**Apache**

Open your virtual hosts file and add the following to your [ProxyPass](http://httpd.apache.org/docs/current/mod/mod_proxy.html#proxypass) directive:

```
timeout=300
```

e.g.

```
ProxyPass / http://127.0.0.1:8080/ timeout=300
```

The ``timeout`` argument accepts any value in seconds and sets the time apache waits for a reply to this value.

### Supervisor

Supervisor is a process manager which makes managing a number of long-running programs a trivial task by providing a consistent interface through which they can be monitored and controlled.

Install and start supervisor:

```bash
sudo apt-get install supervisor
sudo service supervisor restart
```

Create a new configuration (e.g. resolver.conf) for the resolver application

```bash
cd /etc/supervisor/conf.d
sudo touch resolver.conf
sudo nano resolver.conf
```

Copy these lines into the configuration file (or copy the example provided):

```
[program:SERVER_NAME]
directory = RESOLVER_DIRECTORY
command = bash supervisor/start_server.sh
user = RESOLVER_USER
autostart = true
autorestart = true
```

Change the following settings:
* ```SERVER_NAME```: the name of your resolver application (e.g. resolver).
* ```RESOLVER_DIRECTORY```: directory where the resolver application resides (e.g. /srv/resolver).
* ```RESOLVER_USER```: user under which to run the application (must own the RESOLVER_DIRECTORY).

The configuration options for the supervisor script are in `supervisor/resolver.cfg`. Copy `supervisor/resolver.cfg.example` to `supervisor/resolver.cfg` and update the following configuration parameters:
* ```RESOLVER_USER```: user under which to run the application (same as above).
* ```RESOLVER_NAME```: name of the resolver application (same as above).
* ```RESOLVER_DIR```: directory where the resolver application resides (where resolver.cfg is stored) (e.g. /srv/resolver).

```
##
# Configuration settings for supervisor
##
RESOLVER_USER="user"
RESOLVER_NAME="resolver_name"
RESOLVER_DIR="resolver_dir"
```

#### 1.6.x and earlier
Edit the ```start_server.sh``` script in the ```supervisor```-directory and update the following configuration settings:
* ```RESOLVER_USER```: user under which to run the application (same as above).
* ```RESOLVER_NAME```: name of the resolver application (same as above).
* ```PROXY_NAME```: either FQDN or IP-address on which gunicorn must run (e.g. 127.0.0.1 or proxy.resolver.be).
* ```PROXY_PORT```: port on which gunicorn must listen (e.g. 8080).
* ```RESOLVER_DIR```: directory where the resolver application resides (where resolver.cfg is stored) (e.g. /srv/resolver).

Reload supervisor to enact to any updates:

```bash
sudo supervisorctl reread
sudo supervisorctl update
```

**At this point, the resolver service should now be operational and ready to be used.**

## Using the resolver application

Navigate to `http://www.resolver.be/resolver/signin` (substitute by your host/domain). You should be greeted by a login screen. Login using `u:admin` with `p:default`.

**Important: change default password of the admin user account before proceeding to use the application.**

## Running multiple instances simultaneously

### Installation

Running multiple instances simultaneously requires some changes:

Every instance requires its own resolver-directory, with a copy of the entire application. For safety reasons, it is also recommended you create a different user for every instance.

The steps in [the installation instructions](#install) do not change, but every instance must have its own database configured.

As an example, we're configuring two resolver applications, with the public-facing part (the webserver) on ```s1.resolver.be``` and ```s2.resolver.be```. The gunicorn instance is listening on ```s1.proxy.resolver.be``` (port ```8080```) for ```s1.resolver.be``` and ```s2.proxy.resolver.be``` (port ```8081```) for ```s2.resolver.be```.

### Server configuration

#### Gunicorn

Every instance must have its own port configured for gunicorn to listen on. It is impossible to have two gunicorn instances (and thus two resolver instances) to listen on the same port if they are on the same server (e.g. 8080 and 8081). Note that the firewall must allow to connect on these ports.

For reasons of clarity, it is recommended you configure a different (sub)domain for every instance of gunicorn (e.g. s1.proxy.resolver.be and s2.proxy.resolver.be).

Update the Gunicorn configuration file (see [this section](#gunicorn) for more information). Set `proxy_name` to your new subdomain (e.g. `s1.proxy.resolver.be`) and `proxy_port` to your new port (e.g. `8080`).

##### 1.6.x and earlier
Starting the gunicorn server (see [this section](#gunicorn) for more information) thus changes like this:

```
gunicorn -w -b proxy_name:proxy_port resolver:wsgi_app
```

In our example this becomes (for s1):
```
gunicorn -w 4 -b s1.proxy.resolver.be:8080 resolver:wsgi_app
```

And for s2:
```
gunicorn -w 4 -b s2.proxy.resolver.be:8081 resolver:wsgi_app
```

#### HTTP server

##### NGinX

For every new instance, you have to create a new virtual host file for the public-facing part (e.g. s1.resolver.be).

Update the [NGinX virtual host configuration file](#nginx) like this:

```
server {
    listen 80;

    # Make site accessible from http://SITE/
    # This is a catch-all domain configuration.
    # see: http://nginx.org/en/docs/http/server_names.html#miscellaneous_names
    server_name _;

    location / {
        proxy_pass      http://PROXY_NAME:PROXY_PORT/;
        proxy_redirect      off;
        proxy_set_header    Host        $host;
        proxy_set_header    X-Real-IP   $remote_addr;
        proxy_set_header    X-Fowarded-For  $proxy_add_x_forwarded_for;
    }
}
```

Change ```PROXY_NAME``` to either the IP-address or the FQDN of the server your gunicorn instance is listening and ```PROXY_PORT``` to the port it is listening on.

For s1.resolver.be, this becomes:
```
proxy_pass      http://s1.proxy.resolver.be:8080
```

##### Apache

The apache configuration is similar to the NGinX configuration. You must create a new virtual host file for every instance.

The [Apache virtual host configuration file](#apache) must be changed like this:

```
<VirtualHost *:80>
        ServerName SERVER_NAME

        LogLevel warn
        ErrorLog /var/log/apache2/resolver_error.log
        CustomLog /var/log/apache2/alpacafiles/resolver_access.log combined

        ProxyPass / http://PROXY_NAME:PROXY_PORT/
        ProxyPassReverse / http://PROXY_NAME:PROXY_PORT/
        ProxyPreserveHost On
</VirtualHost>
```

```SERVER_NAME``` is the FQDN of the public facing part (e.g. s1.resolver.be); ```PROXY_NAME``` is either the IP-address or the FQDN of the server your gunicorn instance is listening and ```PROXY_PORT``` to the port it is listening on.

For s1.resolver.be, this becomes:

```
<VirtualHost *:80>
        ServerName s1.resolver.be

        LogLevel warn
        ErrorLog /var/log/apache2/resolver_error.log
        CustomLog /var/log/apache2/alpacafiles/resolver_access.log combined

        ProxyPass / http://s1.proxy.resolver.be:8080/
        ProxyPassReverse / http://s1.proxy.resolver.be:8080/
        ProxyPreserveHost On
</VirtualHost>
```

## Deployment to a PaaS environment

### Docker

The application is also made available as a Docker image in the `packed/resolver` repository, and can be used to simplify the installation. The application's webserver is bound to port 80. Once again it is advised to run the application behind another webserver such as Apache or Nginx. See the `apache` and `nginx` directories for example configuration files.

To set up the application using Docker, one can run the following command as an example:
```
docker run -d -p 8080:80 -e "BASE_URL=http://resolver.be" -e "GUNICORN_WORKERS=2" packed/resolver
```
This will download the image, create a new container, execute the application, and forward all requests on `localhost:8080` to the resolver. The container will be configured to use 2 workers for Gunicorn.

Using the `-e` flag it is possible to set environment variables inside the container to configure the application. The `-e "GUNICORN_WORKERS=2"` option can be omitted; in this case the application will fall back to using 4 workers. The `-e "BASE_URL="` is mandatory however, and should be provided for the correct working of the application.

#### Building your own image
It is possible to build a resolver image yourself, as the Dockerfile is provided in the repository.

The image can be built like any other.

### Heroku

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
