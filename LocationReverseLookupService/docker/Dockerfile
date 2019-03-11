FROM node:10-slim

ARG JENKINS_GROUP_ID=1000
ARG JENKINS_USER_ID=1000

RUN addgroup --gid $JENKINS_GROUP_ID jenkins && \
    adduser --uid $JENKINS_USER_ID --gid $JENKINS_GROUP_ID jenkins

