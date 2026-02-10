FROM python:3.11.2

WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ .

COPY infrastructure/docker/entrypoint.sh .
RUN chmod 0755 entrypoint.sh
ENTRYPOINT ["bash", "entrypoint.sh"]
