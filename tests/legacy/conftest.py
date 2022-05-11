import pytest

from databuilder.query_engines.mssql import MssqlQueryEngine
from databuilder.query_engines.spark import SparkQueryEngine

from ..conftest import QueryEngineFixture
from .query_model_convert_to_new import convert as convert_to_new


# This engine fixture wraps the standard query engine fixture and gives it the ability to cope with
# old-style cohort definitions. This allows us to retain these old test cases as a harness while we
# refactor the Query Engine.
class LegacyQueryEngineFixture(QueryEngineFixture):
    def build_engine(self, cohort, **backend_kwargs):
        backend = self.backend(self.database.host_url(), **backend_kwargs)
        return backend.query_engine_class(self._convert(cohort), backend)

    def extract(self, cohort, **backend_kwargs):
        with self._execute(cohort, **backend_kwargs) as results:
            result = list(dict(row) for row in results)
            result.sort(key=lambda i: i["patient_id"])  # ensure stable ordering
            return result

    def _execute(self, cohort, **backend_kwargs):
        return self.build_engine(cohort, **backend_kwargs).execute_query()

    @staticmethod
    def _convert(cohort):
        columns = {
            key: value for key, value in vars(cohort).items() if not key.startswith("_")
        }
        return convert_to_new(columns)


@pytest.fixture(
    scope="session", params=["mssql", pytest.param("spark", marks=pytest.mark.spark)]
)
def engine(request, database, spark_database):
    name = request.param
    if name == "mssql":
        return LegacyQueryEngineFixture(name, database, MssqlQueryEngine)
    elif name == "spark":
        return LegacyQueryEngineFixture(name, spark_database, SparkQueryEngine)
    else:
        assert False
