from cohortextractor import table


class Cohort:
    BASE_INDEX_DATE = None
    population = table("practice_registrations").date_in_range(BASE_INDEX_DATE).exists()
    date = table("clinical_events").first_by("patient_id").get("date")
    event = table("clinical_events").first_by("patient_id").get("code")
