FROM python:3.12-slim-bullseye


COPY requirements.txt ./
COPY src/ ./

# USER python

RUN pip install --no-cache-dir -r requirements.txt

# # configure the container to run in an executed manner
# ENTRYPOINT [ "python" ]
# CMD ["main.py" ]
