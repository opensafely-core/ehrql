# hadolint ignore=DL3007
FROM ghcr.io/opensafely-core/base-docker:latest

# hadolint ignore=DL3008
RUN \
  apt-get update --fix-missing && \
  apt-get install -y --no-install-recommends \
    python3.9 python3.9-dev python3-pip && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.9 1 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.prod.txt /app/requirements.txt
RUN python -m pip install --no-cache-dir --requirement /app/requirements.txt

# hadolint ignore=DL3059
RUN mkdir /workspace
WORKDIR /workspace

# -B: don't write bytecode files
ENTRYPOINT ["python", "-B", "-m", "cohortextractor"]
ENV PYTHONPATH="/app"
COPY cohortextractor /app/cohortextractor
RUN python -m compileall /app/cohortextractor
