# syntax=docker/dockerfile:1
#################################################
#
# Images are structured as shown in this diagram:
# ┌──────────────────┐            ┌──────────────────┐
# │   base-python    ├────────────►     builder      │
# └────────┬─────────┘            └──────────┬───────┘
#          │                                 │
#          │                                 │COPY FROM
#          │     ┌──────────────────┐        │
#          └─────► new-project-base ◄────────┘
#                └────────┬─┬───────┘
#                         │ │
#                         │ │
# ┌──────────────────┐    │ │     ┌──────────────────┐
# │ new-project-prod ◄────┘ └─────► new-project-dev  │
# └──────────────────┘            └──────────────────┘
# The goal of this stages structure is to a) minimise the size of the *prod* image by
# not including build dependencies and b) to make rebuilding the *dev* fast in local
# development, by avoiding invalidating the layer cache every time we change python
# code.
#
#################################################
#
# Create base image with python installed.
# All Dockerfiles should start from the base-docker image
#
# DL3007 ignored because base-docker we specifically always want to build on
# the latest base image, by design.
#
# hadolint ignore=DL3007
# Initial ehrQL layer with just system dependencies installed.
FROM ghcr.io/opensafely-core/base-action:24.04 as base-python

# we are going to use an apt cache on the host, so disable the default debian
# docker clean up that deletes that cache on every apt install
RUN rm -f /etc/apt/apt.conf.d/docker-clean

# use deadsnakes ppa to install a fully working base python installation
# see: https://gist.github.com/tiran/2dec9e03c6f901814f6d1e8dad09528e
# use space efficient utility from base image
RUN --mount=type=cache,target=/var/cache/apt \
    echo "deb https://ppa.launchpadcontent.net/deadsnakes/ppa/ubuntu noble main" > /etc/apt/sources.list.d/deadsnakes-ppa.list && \
    /usr/lib/apt/apt-helper download-file 'https://keyserver.ubuntu.com/pks/lookup?op=get&search=0xf23c5a6cf475977595c89f51ba6932366a755776' /etc/apt/trusted.gpg.d/deadsnakes.asc

# Add Microsoft package archive for installing MSSQL tooling
RUN --mount=type=cache,target=/var/cache/apt \
    echo 'deb [arch=amd64,arm64,armhf signed-by=/usr/share/keyrings/microsoft.asc] https://packages.microsoft.com/ubuntu/24.04/prod noble main' \
      > /etc/apt/sources.list.d/mssql-release.list && \
    /usr/lib/apt/apt-helper download-file \
        "https://packages.microsoft.com/keys/microsoft.asc" \
        /usr/share/keyrings/microsoft.asc

# install any additional system dependencies
# NOTE: ensure .python-version is not excluded in .dockerignore
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=bind,source=.,target=/app \
    /usr/bin/env ACCEPT_EULA=Y  /root/docker-apt-install.sh /app/docker/dependencies.txt "python$(cat /app/.python-version)"

# uv env var documentation: https://docs.astral.sh/uv/reference/environment/
# copy files rather than symlink since the cache and the target are on different filesystems
ENV UV_LINK_MODE=copy
# compile at installation time, not import time
ENV UV_COMPILE_BYTECODE=1
# we are providing python via deadsnakes ppa
# (as we require dynamic linking of openssl for security reasons)
ENV UV_PYTHON_DOWNLOADS=never
# set the directory for the venv
ENV UV_PROJECT_ENVIRONMENT="/opt/venv"


##################################################
#
# Build image
#
# Ok, now we have local base image with python and our system dependencies on.
# We'll use this as the base for our builder image, where we'll build and
# install any python packages needed.
#
# We use a separate, disposable build image to avoid carrying the build
# dependencies into the production image.
FROM base-python as builder

# Install any system build dependencies
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=bind,source=docker/dependencies-build.txt,target=/tmp/dependencies-build.txt \
    /root/docker-apt-install.sh /tmp/dependencies-build.txt

# Install everything in venv for isolation from system python libraries
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /uvx /usr/local/bin/

RUN uv venv

# The cache mount means a) /root/.cache is not in the image, and b) it's preserved
# between docker builds locally, for faster dev rebuild.
# Setting --directory /app lets `uv` detect the pyproject.toml, uv.lock etc.
# Install the project as non-editable so the ehrql entrypoint can be used
RUN --mount=type=cache,target=/root/.cache \
    --mount=type=bind,source=.,target=/app \
    uv sync --frozen --no-dev --no-editable --directory /app


##################################################
#
# Ok, we've built everything we need, build an image with all dependencies but
# no code.
#
# Not including the code at this stage has two benefits:
#
# 1) this image only rebuilds when the handlful of files needed to build
#    the base project image changes. If we do `COPY . /app` now, this will
#    rebuild when *any* file changes.
#
# 2) Ensures we *have* to mount the volume for dev image, as there's no embedded
#    version of the code. Otherwise, we could end up accidentally using the
#    version of the code included when the prod image was built.
FROM base-python as ehrql-base

RUN mkdir -p /app
WORKDIR /app
RUN mkdir /workspace
WORKDIR /workspace

# setup default env vars for all images
# ACTION_EXEC sets the default executable for the entrypoint in the base-action image
ENV VIRTUAL_ENV=/opt/venv/ \
    PATH="/opt/venv/bin:/opt/mssql-tools/bin:$PATH" \
    PYTHONPATH=/app \
    ACTION_EXEC=ehrql \
    PYTHONUNBUFFERED=True \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=0

# copy venv over from builder image. These will have root:root ownership, but
# are readable by all.
COPY --from=builder /opt/venv /opt/venv

##################################################
#
# Production image
#
# Copy code in, add proper metadataFROM ehrql-dependencies as ehrql-base
FROM ehrql-base as ehrql

# Some static metadata for this specific image, as defined by:
# https://github.com/opencontainers/image-spec/blob/master/annotations.md#pre-defined-annotation-keys
# The org.opensafely.action label is used by the jobrunner to indicate this is
# an approved action image to run.
LABEL org.opencontainers.image.title="ehrql" \
      org.opencontainers.image.description="ehrQL action for opensafely.org" \
      org.opencontainers.image.source="https://github.com/opensafely-core/ehrql" \
      org.opensafely.action="ehrql"

# copy application code
COPY ehrql /app/ehrql
COPY bin /app/bin
COPY scripts /app/scripts

# The following build details will change.
# These are the last step to make better use of Docker's build cache,
# avoiding rebuilding image layers unnecessarily.
ARG BUILD_DATE=unknown
LABEL org.opencontainers.image.created=$BUILD_DATE
ARG GITREF=unknown
LABEL org.opencontainers.image.revision=$GITREF
