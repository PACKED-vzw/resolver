##################################
# Dockerfile for Packed Resolver #
# Based on Ubuntu                #
##################################

FROM ubuntu
MAINTAINER PACKED vzw

RUN apt-get update
RUN apt-get -y upgrade
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y tar git wget build-essential vim python python-dev python-virtualenv mysql-server python-mysqldb libmysqlclient-dev
RUN mkdir resolver
WORKDIR /resolver
ADD . .
RUN pip install -r /resolver/requirements.txt
RUN apt-get install -y mysql-server
RUN service mysql start && echo "create database resolver;" | mysql -u root
RUN service mysql start && python initialize.py

# TODO: RUN command to randomize keys etc.

EXPOSE 80
CMD ./run_docker.sh
