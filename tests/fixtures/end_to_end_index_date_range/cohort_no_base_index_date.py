from cohortextractor import table


class Cohort:
    population = table("practice_registrations").date_in_range("2020-01-01").exists()
    date = table("clinical_events").first_by("patient_id").get("date")
    event = table("clinical_events").first_by("patient_id").get("code")
