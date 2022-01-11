from databuilder.contracts.tables import WIP_SimplePatientDemographics
from databuilder.query_model import Table


class Cohort:
    population = Table(WIP_SimplePatientDemographics).exists()
