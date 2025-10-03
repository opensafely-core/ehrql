# syntax=docker/dockerfile:1.2
#################################################
#
# Initial ehrQL layer with just system dependencies installed.
FROM ghcr.io/opensafely-core/base-action:24.04 as ehrql-dependencies


# setup default env vars for all images
# ACTION_EXEC sets the default executable for the entrypoint in the base-action image
ENV VIRTUAL_ENV=/opt/venv/ \
    PYTHONPATH=/app \
    PATH="/opt/venv/bin:/opt/mssql-tools/bin:$PATH" \
    ACTION_EXEC=ehrql \
    PYTHONUNBUFFERED=True \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=0

RUN mkdir /workspace
WORKDIR /workspace

# We are going to use an apt cache on the host, so disable the default debian
# docker clean up that deletes that cache on every apt install
RUN rm -f /etc/apt/apt.conf.d/docker-clean

# Add Microsoft package archive for installing MSSQL tooling
# Add deadsnakes PPA for installing new Python versions
RUN --mount=type=cache,target=/var/cache/apt \
    echo 'deb [arch=amd64,arm64,armhf signed-by=/usr/share/keyrings/microsoft.asc] https://packages.microsoft.com/ubuntu/24.04/prod noble main' \
      > /etc/apt/sources.list.d/mssql-release.list && \
    /usr/lib/apt/apt-helper download-file \
        "https://packages.microsoft.com/keys/microsoft.asc" \
        /usr/share/keyrings/microsoft.asc && \
    echo "deb [signed-by=/usr/share/keyrings/deadsnakes.asc] https://ppa.launchpadcontent.net/deadsnakes/ppa/ubuntu noble main" \
      > /etc/apt/sources.list.d/deadsnakes-ppa.list && \
    /usr/lib/apt/apt-helper download-file \
        'https://keyserver.ubuntu.com/pks/lookup?op=get&search=0xf23c5a6cf475977595c89f51ba6932366a755776' \
        /usr/share/keyrings/deadsnakes.asc


# Install root dependencies, including Python
COPY dependencies.txt /root/dependencies.txt
# use space efficient utility from base image
RUN --mount=type=cache,target=/var/cache/apt \
    /usr/bin/env ACCEPT_EULA=Y /root/docker-apt-install.sh /root/dependencies.txt

#################################################
#
# Next, use the dependencies image to create an image to build dependencies
FROM ehrql-dependencies as ehrql-builder

# install build time dependencies
COPY build-dependencies.txt /root/build-dependencies.txt
RUN /root/docker-apt-install.sh /root/build-dependencies.txt


# install everything in venv for isolation from system python libraries
# hadolint ignore=DL3013,DL3042
RUN --mount=type=cache,target=/root/.cache \
    /usr/bin/python3.11 -m venv /opt/venv && \
    /opt/venv/bin/python -m pip install -U pip setuptools wheel

COPY requirements.prod.txt /root/requirements.prod.txt
# hadolint ignore=DL3042
RUN --mount=type=cache,target=/root/.cache python -m pip install -r /root/requirements.prod.txt

# WARNING clever/ugly python packaging hacks alert
#
# Borrowed (with modifications) from:
# https://github.com/opensafely-core/cohort-extractor/blob/669e2d5d2e/Dockerfile#L54-L84
#
# We could just do `COPY . /app` and then `pip install /app`. However, this is
# not ideal for a number of reasons:
#
# 1) Any changes to the app files will invalidate this and all subsequent
#    layers, causing them to need rebuilding. This would mean basically
#    reinstalling dev dependencies every time.
#
# 2) We want to use the pinned versions of dependencies in
#    requirements.prod.txt rather than the unpinned versions in setup.py.
#
# 3) We want for developers be able to mount /app with their code and it Just
#    Works, without reinstalling anything.
#
# So, we do the following:
#
# 1) Copy a stripped down version of the pyproject.toml file, and install an
#    empty package from it alone (a test ensured the minimal version stays in
#    sync with the full version)
#
# 2) We install it without deps, as they've already been installed.
#
# 3) We have set PYTHONPATH=/app, so that code copied or mounted into /app will
#    be used automatically.
#
# Note: we only really need to install it at all to use setuptools entrypoints.
RUN mkdir /app
COPY pyproject.minimal.toml /app/pyproject.toml
# hadolint ignore=DL3042
RUN --mount=type=cache,target=/root/.cache \
  /opt/venv/bin/python -m pip install --no-deps /app


################################################
#
# A base image with the including the prepared venv and metadata.
FROM ehrql-dependencies as ehrql-base

# Some static metadata for this specific image, as defined by:
# https://github.com/opencontainers/image-spec/blob/master/annotations.md#pre-defined-annotation-keys
# The org.opensafely.action label is used by the jobrunner to indicate this is
# an approved action image to run.
LABEL org.opencontainers.image.title="ehrql" \
      org.opencontainers.image.description="ehrQL action for opensafely.org" \
      org.opencontainers.image.source="https://github.com/opensafely-core/ehrql" \
      org.opensafely.action="ehrql"

COPY --from=ehrql-builder /opt/venv /opt/venv


################################################
#
# Build the actual production image from the base
FROM ehrql-base as ehrql

# Copy app code. This will be automatically picked up by the virtualenv as per
# comment above
COPY ehrql /app/ehrql
RUN python -m compileall /app/ehrql
COPY bin /app/bin
COPY scripts /app/scripts

# The following build details will change.
# These are the last step to make better use of Docker's build cache,
# avoiding rebuilding image layers unnecessarily.
ARG BUILD_DATE=unknown
LABEL org.opencontainers.image.created=$BUILD_DATE
ARG GITREF=unknown
LABEL org.opencontainers.image.revision=$GITREF
