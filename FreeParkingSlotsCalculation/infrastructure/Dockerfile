FROM python:3-slim as build
ENV WORK=/usr/src/app
ARG ARTIFACT_NAME=${BUILD_BUNDLE}
WORKDIR ${WORK}
RUN apt-get update && apt-get -y install zip
COPY . .
RUN sleep 1h
RUN pip install --no-cache-dir -r requirements.txt -t ./src
RUN zip -r ../${BUILD_BUNDLE} .

FROM amazon/aws-cli:2.1.6 as deploy
COPY --from=build ${WORK}/${ARTIFACT_NAME} .
