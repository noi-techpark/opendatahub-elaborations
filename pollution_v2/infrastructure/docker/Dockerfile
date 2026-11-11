# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

FROM python:3.13-slim-bookworm AS base

WORKDIR /app
COPY requirements.txt .
# all the requirements are available as wheels, no compiler is needed
RUN pip install --no-cache-dir --only-binary=:all: -r requirements.txt

# ── Test stage ───────────────────────────────────────────────────────────────
FROM base AS test
COPY src/ /app/
ENV PYTHONPATH=/app
CMD ["python", "-m", "pytest", "tests/", "-v"]

# ── METRo (road weather model) ───────────────────────────────────────────────
# METRo needs the python-libxml2 bindings, so it runs on the Debian system python (not on the python of the jobs).
# See https://framagit.org/metroprojects/metro/-/wikis/Installation_(METRo)
# The compiler is only needed here, and does not end up in the production image.
FROM base AS metro-build
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential python3-dev python3-libxml2 python3-numpy swig gfortran cpio \
    && rm -rf /var/lib/apt/lists/*
COPY weather/metro /metro-src
# numpy.float has been removed from the numpy of Debian
RUN grep -rl 'numpy\.float\b' /metro-src --include='*.py' | xargs sed -i 's/numpy\.float\b/float/g'
ENV PYTHON_INCLUDE=/usr/include/python3.11
RUN /metro-src/setup.sh /usr/local/

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

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 python3-libxml2 python3-numpy libgfortran5 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=metro-build /usr/local/metro /usr/local/metro

COPY src/ /app/
ENV PYTHONPATH=/app

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
