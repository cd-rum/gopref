#!/usr/bin/env bash

set -ex

mkdir -p /app/tmp/image_attachments
mkdir -p /app/tmp/json
mkdir -p /app/tmp/log
mkdir -p /app/tmp/pdf
mkdir -p /app/tmp/sla

mkdir -p /usr/share/fonts/truetype/helvetica
unzip "/app/src.zip" -d /usr/share/fonts/truetype/helvetica
fc-cache -fv
