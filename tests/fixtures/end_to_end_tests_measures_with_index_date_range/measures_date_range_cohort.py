from cohortextractor import Measure, cohort_date_range, table


index_date_range = cohort_date_range(start="2021-01-01", end="2021-03-04")


def cohort(index_date):
    class Cohort:
        _clinical_events = table("clinical_events")
        _registrations = table("practice_registrations").date_in_range(index_date)
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

    return Cohort
