import pytest

from databuilder.query_engines.legacy_mssql import MssqlQueryEngine
from databuilder.query_engines.legacy_spark import SparkQueryEngine

from ..conftest import QueryEngineFixture
from ..lib.mock_backend import MockBackend
from .query_model_convert_to_new import convert as convert_to_new


# This engine fixture wraps the standard query engine fixture and gives it the ability to cope with
# old-style cohort definitions. This allows us to retain these old test cases as a harness while we
# refactor the Query Engine.
class LegacyQueryEngineFixture(QueryEngineFixture):
    def build_engine(self, **engine_kwargs):
        return self.query_engine_class(
            self.database.host_url(), MockBackend(), **engine_kwargs
        )

    def extract(self, cohort, **engine_kwargs):
        cohort = self._convert(cohort)
        return self.extract_qm(cohort, **engine_kwargs)

    def extract_qm(self, cohort, **engine_kwargs):
        query_engine = self.build_engine(**engine_kwargs)
        with query_engine.execute_query(cohort) as results:
            result = list(dict(row) for row in results)
            result.sort(key=lambda i: i["patient_id"])  # ensure stable ordering
            return result

    @staticmethod
    def _convert(cohort):
        columns = {
            key: value for key, value in vars(cohort).items() if not key.startswith("_")
        }
        return convert_to_new(columns)


@pytest.fixture(
    scope="session", params=["mssql", pytest.param("spark", marks=pytest.mark.spark)]
)
def engine(request, mssql_database, spark_database):
    name = request.param
    if name == "mssql":
        return LegacyQueryEngineFixture(name, mssql_database, MssqlQueryEngine)
    elif name == "spark":
        return LegacyQueryEngineFixture(name, spark_database, SparkQueryEngine)
    else:
        assert False
