from databuilder import cohort_date_range
from databuilder.contracts.base import TableContract
from databuilder.query_model import Table


class DummyContract(TableContract):
    pass


index_date_range = cohort_date_range(
    start="2021-01-01", end="2021-03-01", increment="month"
)


def invalid_cohort_function_name(index_date):
    class Cohort:
        population = Table(DummyContract).date_in_range(index_date).exists()
        date = Table(DummyContract).first_by("patient_id").get("date")
        event = Table(DummyContract).first_by("patient_id").get("code")

    return Cohort
