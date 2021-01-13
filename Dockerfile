FROM ubuntu:bionic

RUN apt update && \
    apt install -y --no-install-recommends software-properties-common && \
    add-apt-repository ppa:scribus/ppa && \
    apt update && \
    apt install -y --no-install-recommends python scribus-ng xvfb golang xauth ttf-mscorefonts-installer && \
    apt-get update && \
    apt-get -y upgrade && \
    mkdir /app && \
    fc-cache

COPY . /app
WORKDIR /app

CMD ["./gopref"]
