from databuilder import cohort_date_range
from databuilder.contracts.tables import WIP_ClinicalEvents, WIP_PracticeRegistrations
from databuilder.query_model import Table

index_date_range = cohort_date_range(
    start="2021-01-01", end="2021-03-01", increment="month"
)


def cohort(index_date):
    class Cohort:
        population = Table(WIP_PracticeRegistrations).date_in_range(index_date).exists()
        date = Table(WIP_ClinicalEvents).first_by("patient_id").get("date")
        event = Table(WIP_ClinicalEvents).first_by("patient_id").get("code")

    return Cohort
