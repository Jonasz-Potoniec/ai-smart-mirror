# Event bus implementation as separate docker container

Look into examples forlder for example procducer and consumer codes with message filtering

## Build and run
```sh
# build and tag
docker build -t event-bus-concept .
# or build with custom ports and log level as defaults
docker build --build-arg LOG_LEVEL=debug --build-arg PORT_IN=5500 --build-arg PORT_OUT=5501 -t event-bus-concept .

# run with port mapping
docker run -p 5555:5555 -p 5556:5556 event-bus-concept:latest

# or with custom ports and log level
docker run -p 5500:5500 -p 5501:5501 --env PORT_IN=5500 --env PORT_OUT=5501 --env LOG_LEVEL=debug event-bus-concept:latest
```
