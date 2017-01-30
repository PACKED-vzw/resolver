Installation instructions
=========================

This documents provides instructions to install the Redis on a Ubuntu 14.04 server for use with the Resolver. For more information, see [here](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-redis).

If your distribution includes a Redis package, use your package manager to install it. Take a note of the port the application is using and make sure that it isn't world accessible (as a security precaution).

## Requirements

Redis must be compiled from source and requires the following packages:

```
sudo apt-get install build-essential tcl8.5
```

## Compilation

Download the latest stable release and extract it.

```
curl http://download.redis.io/releases/redis-stable.tar.gz | tar xz
```

Enter the source folder.

```
cd redis-stable
```

Execute the `make` and `make test` commands.

```
make
```

```
make test
```

Finally, if no errors were reported, run `make install`.

```
sudo make install
```


## Configuration

While the Resolver will work with any Redis server, as long as it knows the port and host, it is easiest if it's set up as a background daemon.

From the source directory, change to the `utils` directory and run the install script.

```
cd utils
```

```
sudo ./install_server.sh
```

The script will allow you to customise several configuration options, but if the Resolver is the only application using the Redis server, the defaults are fine.

Take a note of the `port` (by default `6379`) your server will use.

The script has installed Redis (on the port you specified) as a service that can be started and stopped using the `service redis_<port> start/stop` commands.

```
sudo service redis_6379 start
```

To keep your installation secure, it is recommended to configure Redis to only listen on _localhost_ (unless your server is a stand-alone Redis server servicing multiple clients - if so, contact your system administrator).

Open the configuration file (`/etc/redis/<port>.conf`) and set `bind` to `127.0.0.1`. 


