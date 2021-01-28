FROM ubuntu:focal

ENV DEBIAN_FRONTEND noninteractive
ENV TZ Australia/Melbourne

RUN apt-get update && \
    apt install -y --no-install-recommends software-properties-common

RUN add-apt-repository universe && \
    apt update && \
    apt install -y --no-install-recommends python2 python-setuptools scribus xvfb golang git curl unzip && \
    mkdir /app

COPY . /app
WORKDIR /app

RUN curl https://bootstrap.pypa.io/2.6/get-pip.py -o get-pip.py && \
    python2 get-pip.py

RUN pip install -r /app/python/requirements.txt

RUN go get -d ./... && \
    CGO_ENABLED=0 go build -o /app/gopref && \
    bash /app/start.sh

CMD ["bash"]
