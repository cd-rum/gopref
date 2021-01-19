FROM ubuntu:bionic

ENV DEBIAN_FRONTEND noninteractive
ENV TZ Australia/Melbourne

RUN apt update && \
    apt install -y --no-install-recommends software-properties-common && \
    add-apt-repository ppa:scribus/ppa && \
    apt update && \
    apt install -y --no-install-recommends python python-pip scribus-ng xvfb golang git && \
    mkdir /app && \
    fc-cache -f

COPY . /app
WORKDIR /app

RUN go get -d ./...
RUN CGO_ENABLED=0 go build -o /app/gopref
RUN chmod +x /app/python/* && \
    python /app/python/import_or_install.py
RUN /app/gopref &

ENTRYPOINT ["/app/docker-entrypoint.sh"]

