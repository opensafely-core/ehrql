from databuilder import codelist
from databuilder.contracts.base import TableContract
from databuilder.query_model import Table


class DummyContract(TableContract):
    pass


class Cohort:
    _clinical_events = Table(DummyContract)
    _registrations = Table(DummyContract)
    population = _registrations.exists()
    practice = _registrations.first_by("patient_id").get("pseudo_id")
    has_event = _clinical_events.filter(
        "code", is_in=codelist(["abc"], system="ctv3")
    ).first_by("patient_id")
