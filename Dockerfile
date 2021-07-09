# hadolint ignore=DL3007
FROM ghcr.io/opensafely-core/base-docker:latest

RUN \
  apt-get update --fix-missing && \
  apt-get install -y --no-install-recommends \
    python3.9 python3.9-dev python3-pip && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.9 1 && \
    rm -rf /var/lib/apt/lists/*

# hadolint ignore=DL3059
RUN \
  mkdir /app && \
  mkdir /workspace

COPY requirements.prod.txt /app
RUN python -m pip install --no-cache-dir --requirement /app/requirements.prod.txt

COPY cohortextractor /app/cohortextractor

WORKDIR /app
ENTRYPOINT ["python", "-m", "cohortextractor"]
