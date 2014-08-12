##################################
# Dockerfile for Packed Resolver #
# Based on Ubuntu                #
##################################

FROM ubuntu
MAINTAINER PACKED vzw <joris@packed.be>

RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get install -y tar git wget build-essential vim python python-dev python-virtualenv mysql-server python-mysqldb libmysqlclient-dev
RUN mkdir resolver
WORKDIR /resolver
ADD . .
RUN pip install -r /resolver/requirements.txt
RUN service mysql start && echo "create database resolver;" | mysql -u root
RUN rm -f sentinel
RUN rm -f docker_config.py

EXPOSE 80
CMD ./run_docker.sh
