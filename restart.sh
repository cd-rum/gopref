#!/usr/bin/env bash

sudo docker-compose down --rmi all -v && \
  sudo docker-compose build --no-cache && \
  sudo docker-compose up -d --force-recreate


