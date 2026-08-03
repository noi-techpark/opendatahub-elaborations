# SPDX-FileCopyrightText: 2026 NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: CC0-1.0

FROM golang:1.25-bookworm AS base

FROM base AS build-env
WORKDIR /app
COPY src/. .
RUN go mod download
RUN CGO_ENABLED=0 GOOS=linux go build -o /out/ingest ./cmd/ingest
RUN CGO_ENABLED=0 GOOS=linux go build -o /out/train ./cmd/train
RUN CGO_ENABLED=0 GOOS=linux go build -o /out/predict ./cmd/predict

# ── Test stage ───────────────────────────────────────────────────────────────
FROM build-env AS test
CMD ["go", "test", "./..."]

# ── Production stage ─────────────────────────────────────────────────────────
FROM alpine:latest AS build

# supercronic drives the local-dev cron schedule (see entrypoint.sh); in
# production, scheduling is a Kubernetes CronJob per binary and CRON_SCHEDULE
# is left unset, so entrypoint.sh just runs the given command once.
ARG SUPERCRONIC_VERSION=0.2.29
ARG TARGETARCH=amd64
RUN apk add --no-cache curl \
    && curl -fsSL -o /usr/local/bin/supercronic \
        "https://github.com/aptible/supercronic/releases/download/v${SUPERCRONIC_VERSION}/supercronic-linux-${TARGETARCH}" \
    && chmod +x /usr/local/bin/supercronic \
    && apk del curl

WORKDIR /app
COPY --from=build-env /out/ingest /out/train /out/predict ./
COPY infrastructure/docker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
