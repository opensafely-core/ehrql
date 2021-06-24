build-cohort-extractor:
    docker build .

test-e2e: build-cohort-extractor
    pytest tests/end_to_end_tests.py
