# hadolint ignore=DL3007
FROM ghcr.io/opensafely-core/base-docker:latest

# Some static metadata for this specific image, as defined by:
# https://github.com/opencontainers/image-spec/blob/master/annotations.md#pre-defined-annotation-keys
# The org.opensafely.action label is used by the jobrunner to indicate this is
# an approved action image to run.
LABEL org.opencontainers.image.title="databuilder" \
      org.opencontainers.image.description="Data Builder action for opensafely.org" \
      org.opencontainers.image.source="https://github.com/opensafely-core/databuilder" \
      org.opensafely.action="databuilder"

# hadolint ignore=DL3008
RUN \
  apt-get update --fix-missing && \
  apt-get install -y --no-install-recommends \
    python3.9 python3.9-dev python3-pip git && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.9 1 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.prod.txt /app/requirements.txt
RUN python -m pip install --no-cache-dir --requirement /app/requirements.txt

# hadolint ignore=DL3059
RUN mkdir /workspace
WORKDIR /workspace

# -B: don't write bytecode files
ENTRYPOINT ["python", "-B", "-m", "databuilder"]
ENV PYTHONPATH="/app"
COPY pyproject.toml /app/pyproject.toml
COPY databuilder /app/databuilder
RUN --mount=type=bind,target=/app/.git,source=.git python -m pip install --no-cache-dir /app
RUN python -m compileall /app/databuilder
