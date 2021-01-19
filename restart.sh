#!/usr/bin/env bash

sudo docker-compose down --rmi all -v && \
  sudo docker-compose build --no-cache && \
  sudo UID=${UID} GID=${GID} docker-compose up -d --force-recreate


