from contextlib import contextmanager

import pytest

from databuilder.backends import TPPBackend
from databuilder.dsl import Cohort
from tests.lib.util import extract


@pytest.fixture
def cohort(database):
    class AssertingCohort(Cohort):
        def assert_results(self, **results):
            dataset = extract(self, TPPBackend, database)[0]
            for variable, expected_value in results.items():
                assert dataset[variable] == expected_value

    yield AssertingCohort()


@pytest.fixture
def subtest(subtests):
    @contextmanager
    def helper(name, missing_feature=""):
        with subtests.test(msg=name):
            try:
                yield
            except Exception:
                if missing_feature:
                    pytest.xfail(f"DSL feature '{missing_feature}' not implemented")
                raise
            assert (
                not missing_feature
            ), f"Unexpected success, maybe feature '{missing_feature}' has been implemented"

    yield helper
