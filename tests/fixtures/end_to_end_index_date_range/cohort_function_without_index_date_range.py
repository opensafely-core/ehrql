from cohortextractor import table


def cohort():
    class Cohort:
        population = (
            table("practice_registrations").date_in_range("2021-01-01").exists()
        )
        date = table("clinical_events").first_by("patient_id").get("date")
        event = table("clinical_events").first_by("patient_id").get("code")

    return Cohort
