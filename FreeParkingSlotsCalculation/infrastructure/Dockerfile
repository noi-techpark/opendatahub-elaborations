ARG BUILD_BUNDLE="test.zip"
ARG PROJECT_FOLDER="testFolder"
FROM python:3-slim as build
ENV WORK=/usr/src/app
ARG ARTIFACT_NAME=${BUILD_BUNDLE}
WORKDIR ${WORK}
RUN apt-get update && apt-get -y install zip
COPY . .
RUN cd ${PROJECT_FOLDER} && pip install --no-cache-dir -r requirements.txt -t ./src
RUN cd ${PROJECT_FOLDER}/src && zip -r ../${BUILD_BUNDLE} .

FROM amazon/aws-cli:2.1.6 as deploy
COPY --from=build ${WORK}/${ARTIFACT_NAME} .
