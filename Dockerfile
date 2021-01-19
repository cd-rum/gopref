FROM ubuntu:focal

ENV DEBIAN_FRONTEND noninteractive
ENV TZ Australia/Melbourne

RUN apt-get update && \
    apt install -y --no-install-recommends software-properties-common

RUN add-apt-repository universe && \
    apt update && \
    apt install -y --no-install-recommends python2 python2-setuptools scribus xvfb golang git curl && \
    mkdir /app && \
    fc-cache -f

COPY . /app
WORKDIR /app

RUN curl https://bootstrap.pypa.io/get-pip.py --output get-pip.py && \
    python2 get-pip.py

RUN go get -d ./... && \
    CGO_ENABLED=0 go build -o /app/gopref && \
    bash /app/start.sh

CMD ["bash"]
