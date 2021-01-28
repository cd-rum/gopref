#!/usr/bin/env bash

sudo docker container rm $(sudo docker container ls –aq) && \
	sudo docker rmi -f $(sudo docker images -a -q) && \
	sudo docker-compose down --rmi all -v && \
  sudo docker-compose build --no-cache && \
  sudo docker-compose -f production-docker-compose.yml up -d --force-recreate
