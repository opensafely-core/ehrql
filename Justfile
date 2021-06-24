build-cohort-extractor:
    docker build . -t cohort-extractor-v2

test-e2e: build-cohort-extractor
    pytest tests/test_end_to_end.py
