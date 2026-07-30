# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

FROM python:3.13-slim AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc g++ build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Test stage ───────────────────────────────────────────────────────────────
FROM base AS test
COPY src/ /app/
ENV PYTHONPATH=/app
CMD ["python", "-m", "pytest", "tests/", "-v"]

# ── Production stage ─────────────────────────────────────────────────────────
FROM base AS build

ARG SUPERCRONIC_VERSION=0.2.29
ARG TARGETARCH=amd64

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && curl -fsSL -o /usr/local/bin/supercronic \
        "https://github.com/aptible/supercronic/releases/download/v${SUPERCRONIC_VERSION}/supercronic-linux-${TARGETARCH}" \
    && chmod +x /usr/local/bin/supercronic \
    && apt-get purge -y curl \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

COPY src/ /app/
ENV PYTHONPATH=/app

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
