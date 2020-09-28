# gopref

Switched from Vegeta to [Ali](https://github.com/nakabonne/ali).

## load-test

```
ali
```

## develop

```
docker run -d -p 5672:5672 --name gopref-rabbitmq rabbitmq:3
docker stop $(docker ps -a -q)
docker container prune
overmind s
```

## deploy

```
go build .
npm run build
sudo systemctl restart gopref
```
