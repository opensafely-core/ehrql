# hadolint ignore=DL3007
FROM ghcr.io/opensafely-core/base-docker:latest

RUN \
  apt-get update --fix-missing && \
  apt-get install -y --no-install-recommends \
    python3.9 python3.9-dev python3-pip && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.9 1 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.prod.txt /app/requirements.txt
RUN python -m pip install --no-cache-dir --requirement /app/requirements.txt

COPY cohortextractor /app/cohortextractor
ENV PYTHONPATH="/app:${PYTHONPATH}"

RUN mkdir /workspace
WORKDIR /workspace
ENTRYPOINT ["python", "-m", "cohortextractor"]
