#!/usr/bin/env bash

sudo docker-compose down --rmi all -v && \
  sudo docker-compose build --no-cache && \
  sudo docker-compose -f production-docker-compose.yml up -d --force-recreate
