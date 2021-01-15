# gopref

## load-test

```
ali
```

## develop

```
go build .
npm run serve
docker build --tag gopref .
docker-compose up
```

## deploy

```
npm run build
docker build --tag gopref .
docker-compose up
```
