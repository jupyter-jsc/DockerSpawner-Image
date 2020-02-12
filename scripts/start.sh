#!/bin/bash
sed -i -e "s/log_hostname/$HOSTNAME/g" /etc/j4j/J4J_DockerSpawner/uwsgi.ini
uwsgi --ini /etc/j4j/J4J_DockerSpawner/uwsgi.ini
