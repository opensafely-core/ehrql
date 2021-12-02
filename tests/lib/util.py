import databuilder.main
from databuilder import codelist, table
from databuilder.dsl import BoolColumn, EventFrame, IdColumn, IntColumn
from databuilder.query_language import Table


def extract(cohort, backend, database, **backend_kwargs):
    return list(
        databuilder.main.extract(
            cohort, backend(database.host_url(), **backend_kwargs)
        )
    )


class RecordingReporter:
    def __init__(self):
        self.msg = ""

    def __call__(self, msg):
        self.msg = msg


def null_reporter(msg):
    pass


def make_codelist(*codes, system="ctv3"):
    return codelist(codes, system=system)


def iter_flatten(iterable, iter_classes=(list, tuple)):
    """
    Iterate over `iterable` recursively flattening any lists or tuples
    encountered
    """
    for item in iterable:
        if isinstance(item, iter_classes):
            yield from iter_flatten(item, iter_classes)
        else:
            yield item


class OldCohortWithPopulation:
    def __init_subclass__(cls):
        if not hasattr(cls, "population"):  # pragma: no cover
            cls.population = table("practice_registrations").exists()


class MockPatientsTable(EventFrame):
    patient_id = IdColumn("patient_id")
    height = IntColumn("height")

    def __init__(self):
        super().__init__(Table("patients"))


mock_patients = MockPatientsTable()


class MockPositiveTestsTable(EventFrame):
    patient_id = IdColumn("patient_id")
    result = BoolColumn("result")

    def __init__(self):
        super().__init__(Table("positive_tests"))


mock_positive_tests = MockPositiveTestsTable()
