from databuilder.contracts.tables import WIP_ClinicalEvents, WIP_PracticeRegistrations
from databuilder.query_model import Table


def cohort():
    class Cohort:
        population = (
            Table(WIP_PracticeRegistrations).date_in_range("2021-01-01").exists()
        )
        date = Table(WIP_ClinicalEvents).first_by("patient_id").get("date")
        event = Table(WIP_ClinicalEvents).first_by("patient_id").get("code")

    return Cohort
