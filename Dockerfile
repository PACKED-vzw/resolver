##################################
# Dockerfile for Packed Resolver #
# Based on Ubuntu                #
##################################

FROM ubuntu
MAINTAINER PACKED vzw

RUN apt-get update
RUN apt-get -y upgrade
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y tar git wget build-essential vim python python-dev python-virtualenv mysql-server python-mysqldb libmysqlclient-dev
RUN git clone -b docker https://git.nvgeele.be/nvgeele/resolver.git
RUN pip install -r /resolver/requirements.txt
WORKDIR /resolver
RUN service mysql start
RUN echo "create database resolver;" | mysql -u root
RUN python initialize.py
RUN chmod +x run.sh

EXPOSE 80
#CMD ["gunicorn", "-w 2", "-b 0.0.0.0:80", "resolver:app"]
CMD ./run.sh