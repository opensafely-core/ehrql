from databuilder.contracts.tables import WIP_ClinicalEvents, WIP_PracticeRegistrations
from databuilder.query_model import Table


class Cohort:
    population = Table(WIP_PracticeRegistrations).exists()
    date = Table(WIP_ClinicalEvents).first_by("patient_id").get("date")
    event = Table(WIP_ClinicalEvents).first_by("patient_id").get("code")
