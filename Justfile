build-cohort-extractor:
    docker build . -t cohort-extractor-v2

test-e2e ARGS="": build-cohort-extractor
    pytest --tb=native tests/test_end_to_end.py {{ ARGS }}

# run the format checker, sort checker and linter
check:
    black --check .
    isort --check-only --diff .
    flake8

# fix formatting and import sort ordering
fix:
    black .
    isort .
