build-cohort-extractor:
    docker build . -t cohort-extractor-v2

remove-persistent-database:
    docker rm --force cohort-extractor-mssql
    docker network rm cohort-extractor-network

test-unit ARGS="":
    pytest -m "not integration" {{ ARGS }}

test-all ARGS="": build-cohort-extractor
    MODE=slow pytest --cov=cohortextractor --cov=tests {{ ARGS }}

test-all-fast ARGS="":
    MODE=fast pytest --cov=cohortextractor --cov=tests {{ ARGS }}

# run the format checker, sort checker and linter
check:
    black --check .
    isort --check-only --diff .
    flake8

# fix formatting and import sort ordering
fix:
    black .
    isort .
