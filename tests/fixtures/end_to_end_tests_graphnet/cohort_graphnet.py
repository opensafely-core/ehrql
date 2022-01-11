from databuilder.contracts.tables import PatientDemographics
from databuilder.query_model import Table


class Cohort:
    population = Table(PatientDemographics).exists()
    dob = Table(PatientDemographics).first_by("patient_id").get("date_of_birth")
