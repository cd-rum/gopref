# gopref

Switched from Vegeta to [Ali](https://github.com/nakabonne/ali).

## load-test

```
ali
```

## develop

```
npm run build
docker build --tag gopref .
docker-compose up
```

## deploy

```
docker build --tag gopref .
docker-compose up
```
