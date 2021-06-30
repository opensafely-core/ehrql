build-cohort-extractor:
    docker build . -t cohort-extractor-v2

test-e2e ARGS="":
    MODE=fast pytest tests/test_end_to_end.py {{ ARGS }}

test-e2e-slow ARGS="": build-cohort-extractor
    MODE=slow pytest tests/test_end_to_end.py {{ ARGS }}

remove-persistent-database:
    docker rm --force cohort-extractor-mssql
    docker network rm cohort-extractor-network

test-all ARGS="": build-cohort-extractor
    MODE=slow pytest --tb=native --cov=cohortextractor --cov=tests  {{ ARGS }}

test-unit ARGS="":
    pytest --tb=native --ignore=tests/test_end_to_end.py {{ ARGS }}

# run the format checker, sort checker and linter
check:
    black --check .
    isort --check-only --diff .
    flake8

# fix formatting and import sort ordering
fix:
    black .
    isort .
