FROM python:3.8.13-slim-bullseye

COPY requirements.txt ./
COPY src/ ./

RUN pip install --no-cache-dir -r requirements.txt

# # configure the container to run in an executed manner
# ENTRYPOINT [ "python" ]
# CMD ["main.py" ]
