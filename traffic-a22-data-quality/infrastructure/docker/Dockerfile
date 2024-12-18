FROM golang:1.23-bookworm

# install if docker host doesn't has libc6 installed
RUN apt-get update && apt-get install -y libc6

WORKDIR /app

COPY src/main main

CMD [ "./main"]