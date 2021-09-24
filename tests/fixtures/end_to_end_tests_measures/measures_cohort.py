from cohortextractor import Measure, table


class Cohort:
    _clinical_events = table("clinical_events")
    _registrations = table("practice_registrations")
    population = _registrations.exists()
    practice = _registrations.first_by("patient_id").get("pseudo_id")
    has_event = _clinical_events.filter(code="abc").first_by("patient_id")

    measures = [
        Measure(
            id="event_rate",
            numerator="has_event",
            denominator="population",
            group_by="practice",
        )
    ]
