from databuilder import codelist, table


class Cohort:
    _clinical_events = table("clinical_events")
    _registrations = table("practice_registrations")
    population = _registrations.exists()
    practice = _registrations.first_by("patient_id").get("pseudo_id")
    has_event = _clinical_events.filter(code=codelist(["abc"], system="ctv3")).first_by(
        "patient_id"
    )
