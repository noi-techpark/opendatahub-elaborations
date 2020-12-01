FROM python:3-slim
WORKDIR /usr/src/app
RUN apt-get update && apt-get -y install zip
COPY ./ .
ENTRYPOINT ["/bin/bash"]
CMD ["infrastructure/entrypoint.sh"]
