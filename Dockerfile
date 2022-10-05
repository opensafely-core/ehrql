# syntax=docker/dockerfile:1.2
#################################################
#
# Initial databuilder layer with just system dependencies installed.
#
# hadolint ignore=DL3007
FROM ghcr.io/opensafely-core/base-action:latest as databuilder-dependencies


# setup default env vars for all images
# ACTION_EXEC sets the default executable for the entrypoint in the base-action image
ENV VIRTUAL_ENV=/opt/venv/ \
    PYTHONPATH=/app \
    PATH="/opt/venv/bin:/opt/mssql-tools/bin:$PATH" \
    ACTION_EXEC=/app/entrypoint.sh \
    PYTHONUNBUFFERED=True \
    PYTHONDONTWRITEBYTECODE=1


RUN mkdir /workspace
WORKDIR /workspace

# We are going to use an apt cache on the host, so disable the default debian
# docker clean up that deletes that cache on every apt install
RUN rm -f /etc/apt/apt.conf.d/docker-clean

# Using apt-helper means we don't need to install curl or gpg
RUN /usr/lib/apt/apt-helper download-file https://packages.microsoft.com/keys/microsoft.asc /etc/apt/trusted.gpg.d/microsoft.asc && \
    /usr/lib/apt/apt-helper download-file https://packages.microsoft.com/config/ubuntu/20.04/prod.list /etc/apt/sources.list.d/mssql-release.list

# Install root dependencies, including python3.9
COPY dependencies.txt /root/dependencies.txt
# use space efficient utility from base image
RUN --mount=type=cache,target=/var/cache/apt \
    /usr/bin/env ACCEPT_EULA=Y /root/docker-apt-install.sh /root/dependencies.txt

#################################################
#
# Next, use the dependencies image to create an image to build dependencies
FROM databuilder-dependencies as databuilder-builder

# install build time dependencies
COPY build-dependencies.txt /root/build-dependencies.txt
RUN /root/docker-apt-install.sh /root/build-dependencies.txt


# install everything in venv for isolation from system python libraries
# hadolint ignore=DL3013,DL3042
RUN --mount=type=cache,target=/root/.cache \
    /usr/bin/python3.9 -m venv /opt/venv && \
    /opt/venv/bin/python -m pip install -U pip setuptools wheel

COPY requirements.prod.txt /root/requirements.prod.txt
# hadolint ignore=DL3042
RUN --mount=type=cache,target=/root/.cache python -m pip install -r /root/requirements.prod.txt

################################################
#
# A base image with the including the prepared venv and metadata.
FROM databuilder-dependencies as databuilder-base

# Some static metadata for this specific image, as defined by:
# https://github.com/opencontainers/image-spec/blob/master/annotations.md#pre-defined-annotation-keys
# The org.opensafely.action label is used by the jobrunner to indicate this is
# an approved action image to run.
LABEL org.opencontainers.image.title="databuilder" \
      org.opencontainers.image.description="Data Builder action for opensafely.org" \
      org.opencontainers.image.source="https://github.com/opensafely-core/databuilder" \
      org.opensafely.action="databuilder"

COPY --from=databuilder-builder /opt/venv /opt/venv

RUN mkdir /app

################################################
#
# Build the actual production image from the base
FROM databuilder-base as databuilder

# copy app code. This will be automatically picked up by the virtual env as per
# comment above
COPY entrypoint.sh /app/entrypoint.sh
COPY databuilder /app/databuilder
RUN python -m compileall /app/databuilder

################################################
#
# Development image that includes test dependencies and mounts the code in
FROM databuilder as databuilder-dev

# Install dev dependencies
COPY requirements.dev.txt /root/requirements.dev.txt
# hadolint ignore=DL3042
RUN --mount=type=cache,target=/root/.cache python -m pip install -r /root/requirements.dev.txt
