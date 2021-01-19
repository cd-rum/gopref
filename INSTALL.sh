#! /bin/bash

mkdir -p /usr/share/fonts/truetype/helvetica
unzip "src.zip" -d /usr/share/fonts/truetype/helvetica
fc-cache -fv
